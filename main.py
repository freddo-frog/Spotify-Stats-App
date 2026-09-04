#importing...
from flask import Flask, redirect, request, session, render_template, url_for
from urllib.parse import urlencode
import os
from dotenv import load_dotenv
import requests
import json 
import time
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
        "scope": "user-top-read user-read-recently-played"
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
    session["refresh_token"] = tokens["refresh_token"]
    session["expires_at"] = time.time() + tokens["expires_in"]
    return redirect(url_for("home"))

@app.route("/top-tracks")
def get_tracks():
    token = get_valid_token()
    time_range = request.args.get("time_range", "medium_term")
    params = {
        "time_range": time_range
    }
    tracks = requests.get("https://api.spotify.com/v1/me/top/tracks", headers={"Authorization": f"Bearer {token}"}, params=params)
    data = tracks.json()
    results = []
    for item in data["items"]:
        song_name = item["name"]
        artist_name = item["artists"][0]["name"]
        results.append(f"{song_name} - {artist_name}")
    return render_template("top_tracks.html", results =results)

@app.route("/top-artists")
def get_artists():
    token = get_valid_token()
    time_range = request.args.get("time_range", "medium_term")
    params = {
        "time_range": time_range
    }
    artists = requests.get("https://api.spotify.com/v1/me/top/artists",headers={"Authorization": f"Bearer {token}"}, params=params)
    data = artists.json()
    results = []
    for item in data["items"]:
        artist_name = item["name"]
        results.append(f"{artist_name}")
    return render_template("top_artists.html", results=results)

@app.route("/recently-played")
def get_recently_played():
    token = get_valid_token()
    recents = requests.get("https://api.spotify.com/v1/me/player/recently-played", headers={"Authorization": f"Bearer {token}"})
    data = recents.json()
    results = []
    for item in data["items"]:
        song_name = item["track"]["name"]
        artist_name = item["track"]["artists"][0]["name"]
        time = item["played_at"]
        results.append(f"{song_name} - {artist_name}\n played at: {time}")
    return render_template("recently_played.html", results=results)

def get_valid_token():
    access_token = session.get("access_token")
    refresh_token = session.get("refresh_token")
    expires_at = session.get("expires_at")
    if time.time() >= expires_at:
        token_params_refresh = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
            "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET")
        }
        response = requests.post("https://accounts.spotify.com/api/token", data=token_params_refresh)
        token = response.json()
        session["expires_at"] = time.time() + token["expires_in"]
        session["access_token"] = token["access_token"]
        new_token = session["access_token"]
        return new_token

    else:
        return access_token

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)