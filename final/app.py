import base64
import requests
from flask import Flask, request, render_template

app = Flask(__name__)

CLIENT_ID = "df33ce08fa674f1a8b659d7e14105ff4"
CLIENT_SECRET = "3075449b9e4e48c3bbe4a0351d814e75"

# Get an access token using Client Credentials (NO LOGIN)
def get_access_token():
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials"},
    )

    return response.json().get("access_token")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    track_url = request.form["track"]

    # Extract track ID from URL or input
    if "track/" in track_url:
        track_id = track_url.split("track/")[1].split("?")[0]
    else:
        track_id = track_url.strip()

    token = get_access_token()

    response = requests.get(
        f"https://api.spotify.com/v1/audio-features/{track_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    features = response.json()
    print("FEATURES:", features)

    return render_template("results.html", features=features)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
