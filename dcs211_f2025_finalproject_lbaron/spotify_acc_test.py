from dotenv import load_dotenv
load_dotenv()

import spotipy
from spotipy.oauth2 import SpotifyOAuth

def create_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope="user-read-private playlist-read-private playlist-read-collaborative",
        redirect_uri="http://127.0.0.1:8888/callback"
    ))

def main():
    sp = create_spotify_client()
    user = sp.current_user()

    print("Authenticated as:")
    print("  Display Name:", user.get("display_name"))
    print("  User ID:", user.get("id"))

if __name__ == "__main__":
    main()
