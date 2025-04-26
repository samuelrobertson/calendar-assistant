from flask import Flask, redirect, request
import os
import requests
import urllib.parse

app = Flask(__name__)

# Set these with your real credentials
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "https://de94fbf8-f73f-4f6b-81e2-02d844d08046-00-3kwv0gecvd9ma.janeway.replit.dev/callback"

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]

@app.route("/")
def index():
    # Step 1: Redirect to Google's OAuth 2.0 server
    query_params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"{AUTH_URL}?{urllib.parse.urlencode(query_params)}"
    return redirect(url)

@app.route("/callback")
def callback():
    # Step 2: Google redirects back with ?code=
    code = request.args.get("code")

    # Step 3: Exchange code for tokens
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    res = requests.post(TOKEN_URL, data=data)
    tokens = res.json()

    return f"""
    <h1>OAuth Success!</h1>
    <pre>{tokens}</pre>
    <p>Copy your access_token and refresh_token into Replit secrets or a .env file.</p>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
