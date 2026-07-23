#importing...
from flask import Flask, redirect, request, session
from urllib.parse import urlencode
import os
from dotenv import load_dotenv
import requests
#=== log in ===

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

@app.route("/login")
def login():
    params = {
        "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
        "redirect_uri": "http://127.0.0.1:5000/callback",
        "response_type": "code",
        "scope": "user-top-read"
    }
    auth_url = "https://accounts.spotify.com/authorize?" + urlencode(params)
    return redirect(auth_url)

@app.route("/callback")
def get_info():
    code = request.args.get("code")
    token_params = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://127.0.0.1:5000/callback",
        "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
        "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET")
    }
    response = requests.post("https://accounts.spotify.com/api/token", data=token_params)
    tokens = response.json()
    session["access_token"] = tokens["access_token"]
    return "Logged in!"
    

if __name__ == "__main__":
    app.run(debug=True)