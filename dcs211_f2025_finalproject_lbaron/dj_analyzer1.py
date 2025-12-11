# ============================================================
# DJ ANALYZER — FINAL, STABLE, FULLY WORKING VERSION
# ============================================================
import os
from dotenv import load_dotenv
load_dotenv()
print("CLIENT ID =", os.getenv("SPOTIPY_CLIENT_ID"))
print("SECRET =", os.getenv("SPOTIPY_CLIENT_SECRET"))
print("REDIRECT =", os.getenv("SPOTIPY_REDIRECT_URI"))

from spotipy.oauth2 import SpotifyOAuth
import spotipy


import re
import pandas as pd
from dotenv import load_dotenv
from spotipy.exceptions import SpotifyException
import spotipy
from spotipy.oauth2 import SpotifyOAuth

import webbrowser
webbrowser.register(
    'chrome',
    None,
    webbrowser.BackgroundBrowser("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
)
webbrowser.get('chrome')


# Load environment variables (client ID, secret, redirect URI)
load_dotenv()


# ============================================================
# 1. Spotify Client Authentication
# ============================================================

def create_spotify_client():


    # CLEAN ASCII SCOPES (this was the real issue)
    scope = "playlist-read-private playlist-read-collaborative playlist-read-public"

    auth_manager = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope=scope,
        cache_path=".spotify_cache"
    )

    return spotipy.Spotify(auth_manager=auth_manager)


# ============================================================
# 2. DataFrame Initialization
# ============================================================

def create_empty_playlist_df():
    """Create an empty DataFrame with MultiIndex (track_name, artist)."""
    index = pd.MultiIndex.from_tuples([], names=["track_name", "artist"])
    df = pd.DataFrame(
        index=index,
        columns=["track_id", "tempo", "key", "energy", "danceability",
                 "loudness", "valence", "duration_ms"]
    )
    return df


# ============================================================
# 3. ID Extraction Utilities
# ============================================================

def extract_track_id(url):
    """Extract track ID from a Spotify track URL."""
    if "open.spotify.com/track/" in url:
        return url.split("/track/")[1].split("?")[0]
    return None


def extract_playlist_id(raw):
    """Extract playlist ID from URLs or raw IDs."""
    if not raw:
        return None

    raw = raw.strip()

    if raw.startswith("spotify:playlist:"):
        return raw.split("spotify:playlist:")[1]

    m = re.search(r"playlist/([A-Za-z0-9]+)", raw)
    if m:
        return m.group(1)

    if re.fullmatch(r"[A-Za-z0-9]+", raw):
        return raw

    return None


# ============================================================
# 4. SINGLE TRACK IMPORT
# ============================================================

def fetch_track_from_spotify(sp, query):
    """Imports a single track via URL or search query."""
    try:
        if "open.spotify.com/track" in query:
            track_id = extract_track_id(query)
        else:
            results = sp.search(q=query, limit=1, type="track")
            if not results["tracks"]["items"]:
                print("No track found.")
                return None
            track_id = results["tracks"]["items"][0]["id"]

        track = sp.track(track_id)
        features = sp.audio_features(track_id)[0]

        if track is None or features is None:
            print("Track has no audio features.")
            return None

        return {
            "track_name": track["name"],
            "artist": track["artists"][0]["name"],
            "track_id": track_id,
            "tempo": features["tempo"],
            "key": features["key"],
            "energy": features["energy"],
            "danceability": features["danceability"],
            "loudness": features["loudness"],
            "valence": features["valence"],
            "duration_ms": features["duration_ms"]
        }

    except Exception as e:
        print("Spotify error:", e)
        return None


# ============================================================
# 5. PLAYLIST IMPORT ENGINE
# ============================================================

def import_playlist_from_spotify(sp, url):
    """Fetch all valid tracks + audio features from any playlist."""

    playlist_id = extract_playlist_id(url)
    if playlist_id is None:
        print("ERROR: Invalid playlist URL.")
        return []

    print(f"\nImporting playlist: {playlist_id}\n")

    all_tracks = []
    limit = 100
    offset = 0

    try:
        while True:
            response = sp.playlist_items(
                playlist_id,
                offset=offset,
                limit=limit,
                additional_types=["track"]
            )

            items = response.get("items", [])
            if not items:
                break

            valid_ids = []
            track_objs = []

            for itm in items:
                track = itm.get("track")
                if not track:
                    continue

                tid = track.get("id")
                if tid is None:
                    print(f"Skipping unsupported track: {track.get('name')}")
                    continue

                valid_ids.append(tid)
                track_objs.append(track)

            features_map = {}

            if valid_ids:
                try:
                    features_list = sp.audio_features(valid_ids)
                    for tid, feat in zip(valid_ids, features_list):
                        if feat:
                            features_map[tid] = feat
                except SpotifyException as e:
                    print("Audio feature fetch failure:", e)

            for track in track_objs:
                tid = track["id"]
                feat = features_map.get(tid)

                if feat is None:
                    print(f"Skipping track without features: {track['name']}")
                    continue

                track_data = {
                    "track_name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "track_id": tid,
                    "tempo": feat["tempo"],
                    "key": feat["key"],
                    "energy": feat["energy"],
                    "danceability": feat["danceability"],
                    "loudness": feat["loudness"],
                    "valence": feat["valence"],
                    "duration_ms": feat["duration_ms"]
                }

                all_tracks.append(track_data)

            offset += limit
            if response.get("next") is None:
                break

    except SpotifyException as e:
        print("ERROR: Spotify refused the request:", e)
        return []

    return all_tracks


# ============================================================
# 6. Add Track to DataFrame
# ============================================================

def add_track_to_df(df, data):
    """Insert a track dictionary into the playlist DataFrame."""
    key = (data["track_name"], data["artist"])
    df.loc[key] = [
        data["track_id"], data["tempo"], data["key"], data["energy"],
        data["danceability"], data["loudness"], data["valence"],
        data["duration_ms"]
    ]
    print(f"Added: {data['track_name']} — {data['artist']}")
    return df


# ============================================================
# 7. Display & Query Functions
# ============================================================

def show_playlist(df):
    print("\n=== PLAYLIST DATA ===\n")
    if df.empty:
        print("Playlist is empty.\n")
    else:
        print(df)
    print()


def query_track(df):
    name = input("Track name: ").strip()
    artist = input("Artist: ").strip()
    key = (name, artist)

    if key not in df.index:
        print("\nTrack not found.\n")
    else:
        print("\nTrack data:\n")
        print(df.loc[key])
    print()


# ============================================================
# 8. MAIN PROGRAM MENU
# ============================================================

def main():
    print("=== DJ Playlist Analyzer ===")
    print("Program starting...")

    df = create_empty_playlist_df()
    sp = create_spotify_client()

    while True:
        print("\n=== DJ Playlist Analyzer ===")
        print("1. Add track from Spotify")
        print("2. Import playlist from Spotify")
        print("3. Show playlist data")
        print("4. Query a track")
        print("5. Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            query = input("Enter Spotify track URL or search term: ").strip()
            track_data = fetch_track_from_spotify(sp, query)

            if track_data:
                df = add_track_to_df(df, track_data)
            else:
                print("Could not retrieve track.")

        elif choice == "2":
            url = input("\nEnter Spotify playlist URL: ").strip()
            tracks = import_playlist_from_spotify(sp, url)

            print(f"\nFound {len(tracks)} valid tracks.\n")

            for t in tracks:
                df = add_track_to_df(df, t)

            print("\n=== Playlist Imported Successfully ===\n")
            show_playlist(df)

        elif choice == "3":
            show_playlist(df)

        elif choice == "4":
            query_track(df)

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please select 1–5.")


# ============================================================
# Program Entry Point
# ============================================================

if __name__ == "__main__":
    main()



