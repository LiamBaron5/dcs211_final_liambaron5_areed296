import pandas as pd

import spotipy
from spotipy.oauth2 import SpotifyOAuth

def create_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope="playlist-read-private,playlist-read-collaborative"
    ))

# ============================================================
# DataFrame Setup
# ============================================================

def create_empty_playlist_df():
    """Create an empty DataFrame with all expected columns."""
    df = pd.DataFrame(columns=[
        "track_name",
        "artist",
        "track_id",
        "tempo",
        "key",
        "energy",
        "danceability",
        "loudness",
        "valence",
        "duration_ms"
    ])
    
    # MultiIndex (track_name, artist) makes lookups very safe
    df.set_index(["track_name", "artist"], inplace=True)
    return df

####
# ============================================================
# Adding Track Data (Placeholder — No Spotify API yet)
# ============================================================

def add_track_to_df(df, track_name, artist, tempo, key, energy, danceability, loudness, valence, duration_ms):
    """Adds a single track’s data to the playlist DataFrame."""
    
    df.loc[(track_name, artist), :] = {
        "track_id": None,  # placeholder until API implementation
        "tempo": tempo,
        "key": key,
        "energy": energy,
        "danceability": danceability,
        "loudness": loudness,
        "valence": valence,
        "duration_ms": duration_ms
    }
    
    print(f"\nAdded track: {track_name} — {artist}")
    return df


# ============================================================
# Display & Query Functions
# ============================================================

def show_playlist(df):
    if df.empty:
        print("\nPlaylist is empty.\n")
    else:
        print("\nCurrent Playlist Data:\n")
        print(df)
        print()


def query_track(df):
    """User looks up a track by name + artist."""
    name = input("Enter track name: ")
    artist = input("Enter artist: ")
    
    try:
        print("\nTrack Information:\n")
        print(df.loc[(name, artist)])
        print()
    except KeyError:
        print("\nTrack not found.\n")


# ============================================================
# Menu System
# ============================================================




def main():
    df = create_empty_playlist_df()
    
    while True:
        choice = main_menu()
        
        if choice == "1":
            # Manual input (simulating data until Spotify API)
            name = input("\nTrack name: ")
            artist = input("Artist: ")
            tempo = float(input("Tempo (BPM): "))
            key = int(input("Key (0–11): "))
            energy = float(input("Energy (0–1): "))
            danceability = float(input("Danceability (0–1): "))
            loudness = float(input("Loudness (dB): "))
            valence = float(input("Valence (0–1): "))
            duration_ms = int(input("Duration (ms): "))
            
            df = add_track_to_df(df, name, artist, tempo, key, energy,
                                 danceability, loudness, valence, duration_ms)
        
        elif choice == "2":
            show_playlist(df)
        
        elif choice == "3":
            query_track(df)
        
        elif choice == "4":
            print("\nExiting program.\n")
            break
        
        else:
            print("\nInvalid choice. Try again.\n")


if __name__ == "__main__":
    main()
