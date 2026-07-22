#importing...
from flask import Flask, redirect
from urllib.parse import urlencode
import os
from dotenv import load_dotenv
import requests 
#=== log in ===

load_dotenv()
app = Flask(__name__)

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
if __name__ == "__main__":
    app.run(debug=True)