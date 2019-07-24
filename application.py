from flask import Flask
app = Flask(__name__)

import json
from flask import Flask, request, redirect, g, render_template
import requests
from urllib.parse import quote

# App Variables
num_tracks = "10"
tracks = []

#  Client Keys
CLIENT_ID = "fca9ceb166874160940a6c1e3a38ee09"
CLIENT_SECRET = "d5fb2307efff4aeca1d5f0837c5fb737"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "https://hackathonproject.azurewebsites.net"
PORT = 5000
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "user-top-read"
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "client_id": CLIENT_ID
}

@app.route("/")
def index():
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)

@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}
    
    # Get top tracks for current user
    top_tracks_payload = {
        "time_range" : "long_term",
        "limit" : num_tracks
    }
    
    top_tracks_params = "&".join(["{}={}".format(key, quote(val)) for key, val in top_tracks_payload.items()])
    top_tracks_api_endpoint = "{}/me/top/tracks".format(SPOTIFY_API_URL)
    top_tracks_response = requests.get(top_tracks_api_endpoint, headers=authorization_header, params = top_tracks_params)
    top_tracks = json.loads(top_tracks_response.text)["items"]
    
    # format tracks into array of name-artists pairs 
    for track in top_tracks:
        artists_names = ""
        name = track["name"]
        artists = track["artists"]
        for artist in artists:
            artists_names = artists_names + " " + artist["name"]
        print(artists_names)
        tracks.append([name, artists_names])

    print(tracks)

    return render_template("index.html", sorted_array=tracks)


if __name__ == "__main__":
    app.run(debug=True, port=PORT)	
 	
