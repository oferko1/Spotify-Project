import os
import time
import base64
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    raise RuntimeError(
        "Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET. "
        "Set them in .env or your environment."
    )

app = Flask(__name__)

# Simple in-memory token cache
token_cache = {
    "access_token": None,
    "expires_at": 0.0  # epoch seconds
}


def get_access_token() -> str:
    """Get (and cache) a Spotify access token using client credentials."""
    now = time.time()
    if token_cache["access_token"] and now < token_cache["expires_at"] - 5:
        return token_cache["access_token"]

    auth_header = base64.b64encode(
        f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode("utf-8")
    ).decode("utf-8")

    resp = requests.post(
        SPOTIFY_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    access_token = data["access_token"]
    expires_in = data.get("expires_in", 3600)

    token_cache["access_token"] = access_token
    token_cache["expires_at"] = now + expires_in

    return access_token


def search_artist_by_name(name: str, access_token: str):
    """Return the first matching artist object, or None if not found."""
    resp = requests.get(
        f"{SPOTIFY_API_BASE}/search",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"q": name, "type": "artist", "limit": 1},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    items = data.get("artists", {}).get("items", [])
    return items[0] if items else None


def get_top_tracks(artist_id: str, market: str, access_token: str):
    """Return the list of top track objects for the artist."""
    resp = requests.get(
        f"{SPOTIFY_API_BASE}/artists/{artist_id}/top-tracks",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"market": market},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("tracks", [])


def normalize_track(track: dict) -> dict:
    """Trim Spotify's track JSON down to the fields we care about."""
    return {
        "title": track.get("name"),
        "id": track.get("id"),
        "artists": [a.get("name") for a in track.get("artists", [])],
        "preview_url": track.get("preview_url"),
        "popularity": track.get("popularity"),
        "external_url": track.get("external_urls", {}).get("spotify"),
    }


@app.route("/")
def root():
    return (
        "Spotify Artist Top Tracks API\n"
        "Try: /top-tracks?artist=dua lipa&market=US\n"
    )


@app.route("/top-tracks", methods=["GET"])
def top_tracks():
    artist_query = (request.args.get("artist") or "").strip()
    market = (request.args.get("market") or "US").upper()

    if not artist_query:
        return (
            jsonify({"error": "Missing required query parameter 'artist'."}),
            400,
        )

    try:
        access_token = get_access_token()

        artist = search_artist_by_name(artist_query, access_token)
        if artist is None:
            return (
                jsonify({"error": f"No artist found for '{artist_query}'."}),
                404,
            )

        tracks = get_top_tracks(artist["id"], market, access_token)
        payload = {
            "artist": {
                "name": artist.get("name"),
                "id": artist.get("id"),
            },
            "market": market,
            "trackCount": len(tracks),
            "tracks": [normalize_track(t) for t in tracks],
        }
        return jsonify(payload)

    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else 502
        return (
            jsonify(
                {
                    "error": "Upstream Spotify API error.",
                    "status": status,
                    "details": e.response.json()
                    if e.response is not None and e.response.headers.get("content-type", "").startswith("application/json")
                    else str(e),
                }
            ),
            status,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "error": "Internal server error.",
                    "details": str(e),
                }
            ),
            500,
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "3000"))
    app.run(host="0.0.0.0", port=port, debug=True)
