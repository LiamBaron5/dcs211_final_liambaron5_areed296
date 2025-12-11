import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")


# ----------------------------------------------------
# Get access token using Client Credentials Flow
# ----------------------------------------------------
def get_access_token():
    url = "https://accounts.spotify.com/api/token"
    auth_header = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)

    data = {"grant_type": "client_credentials"}
    r = requests.post(url, auth=auth_header, data=data)

    if r.status_code != 200:
        print("❌ Failed to get access token:", r.text)
        return None

    return r.json()["access_token"]


# ----------------------------------------------------
# Search for a track by name OR extract ID from URL
# ----------------------------------------------------
def get_track_id(token, user_input):
    # If input is a URL
    if "spotify.com/track" in user_input:
        return user_input.split("/")[-1].split("?")[0]

    # Otherwise search by track name
    url = "https://api.spotify.com/v1/search"
    params = {"q": user_input, "type": "track", "limit": 1}
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(url, headers=headers, params=params)
    data = r.json()

    try:
        return data["tracks"]["items"][0]["id"]
    except:
        print("❌ Could not find track:", user_input)
        return None


# ----------------------------------------------------
# Get audio features (BPM, key, mode, etc.)
# ----------------------------------------------------
def get_audio_features(token, track_id):
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print("❌ Error getting audio features:", r.text)
        return None

    return r.json()


# ----------------------------------------------------
# Convert Spotify key + mode → musical key string
# ----------------------------------------------------
KEY_MAP = {
    0: "C", 1: "C♯/D♭", 2: "D", 3: "D♯/E♭", 4: "E",
    5: "F", 6: "F♯/G♭", 7: "G", 8: "G♯/A♭",
    9: "A", 10: "A♯/B♭", 11: "B"
}


def format_key(features):
    if features["key"] == -1:
        return "Unknown"

    base = KEY_MAP[features["key"]]
    return base + (" major" if features["mode"] == 1 else " minor")


# ----------------------------------------------------
# Print DJ-useful info
# ----------------------------------------------------
def print_dj_info(f):
    print("\n🎧 DJ Track Analysis")
    print("------------------------")
    print("BPM:", f["tempo"])
    print("Key:", format_key(f))
    print("Danceability:", f["danceability"])
    print("Energy:", f["energy"])
    print("Valence (mood):", f["valence"])
    print("Liveness:", f["liveness"])
    print("Instrumentalness:", f["instrumentalness"])
    print("------------------------\n")


# ----------------------------------------------------
# Main Program Loop
# ----------------------------------------------------
def main():
    print("Requesting Spotify access token...")
    token = get_access_token()

    if token is None:
        return

    while True:
        print("1. Analyze a track")
        print("2. Exit")
        choice = input("Enter choice: ")

        if choice == "2":
            break

        user_input = input("Enter track URL, ID, or name: ")
        track_id = get_track_id(token, user_input)

        if track_id:
            features = get_audio_features(token, track_id)
            if features:
                print_dj_info(features)
        print()


if __name__ == "__main__":
    main()


