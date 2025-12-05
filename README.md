# Spotify-Project
API Semester Project

Spotify Artist Top Tracks API

A simple REST API that lets a user enter the name of any music artist (like “Dua Lipa” or “Drake”) and returns that artist’s Top Tracks from the Spotify Web API in clean, easy-to-read JSON format.

This project demonstrates calling an external API, processing the response, and returning simplified JSON from your own service.

FEATURES

Search for an artist by name

Automatically fetch the artist’s Spotify ID

Retrieve the artist’s Top Tracks

Return simplified JSON fields:

Song title

Artists

Popularity

Preview URL

Spotify track link

REQUIREMENTS

Python 3.10+

Spotify Developer Client ID & Client Secret

Flask, requests, python-dotenv

All dependencies are listed in Proj_Requirements.txt.

SETUP

Navigate to the project folder:
cd ~/Desktop/spotify-top-tracks

Create a virtual environment:
python3 -m venv venv
source venv/bin/activate

Install dependencies:
pip install -r Proj_Requirements.txt

Create a .env file with your Spotify credentials:

SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
FLASK_ENV=development
PORT=3000

Client ID and Secret can be obtained from:
https://developer.spotify.com/dashboard

RUNNING THE API

Start the server:

source venv/bin/activate
python3 API_app.py

The server will run on:
http://localhost:3000

API USAGE

Endpoint:
GET /top-tracks?artist={artist_name}&market={country_code}

Example:
http://localhost:3000/top-tracks?artist=dua
 lipa&market=US

Example JSON Response:
{
"artist": {
"name": "Dua Lipa",
"id": "..."
},
"market": "US",
"trackCount": 10,
"tracks": [
{
"title": "Levitating",
"artists": ["Dua Lipa"],
"preview_url": "...",
"popularity": 89,
"external_url": "https://open.spotify.com/track/
..."
}
]
}

HOW IT WORKS

The API receives the artist name from the URL.

It requests a Spotify access token using Client Credentials Flow.

It searches Spotify for the artist ID.

It fetches the artist’s Top Tracks using that ID.

It normalizes Spotify’s data and returns clean JSON.

FILE STRUCTURE

spotify-top-tracks/

API_app.py

Proj_Requirements.txt

.env

venv/

NOTES

Redirect URIs are required by Spotify but not used in this project.

No user login or OAuth redirect is needed.
