import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

print("CLIENT ID =", CLIENT_ID)
print("CLIENT SECRET =", CLIENT_SECRET)

auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

res = requests.post(
    "https://accounts.spotify.com/api/token",
    data={"grant_type": "client_credentials"},
    headers={"Authorization": f"Basic {auth}"}
)

print("\nRAW TOKEN RESPONSE:")
print(res.text)
