import asyncio
from fastapi import FastAPI, Query, Depends, Request, HTTPException, Header
from typing import List
from auth.spotify_auth import get_spotify_oauth
from utils.playlist_utils import get_all_tracks_from_playlists, create_playlist_and_add_tracks, get_audio_features_for_tracks, get_playlist_tracks
import spotipy
import httpx
from fastapi.responses import RedirectResponse
from utils.gemini_utils import classify_songs_by_mood, hello_model,classify_song_ids_by_mood  
import json
from fastapi.responses import JSONResponse
import re

app = FastAPI()

def escape_for_prompt(s: str):
    return s.replace("\\", "\\\\").replace("\"", "\\\"")

def format_gemini_response(raw_response: str):
    try:
        # Step 1: Extract JSON block from markdown
        match = re.search(r"```(?:json)?\s*(\[\s*{.*?}\s*])\s*```", raw_response, re.DOTALL)
        if not match:
            raise ValueError("Could not find a valid JSON block")

        json_str = match.group(1)

        # Step 2: Replace problematic escape characters
        json_str = json_str.replace('\\"', '"')   # remove escaped quotes inside strings
        json_str = json_str.replace('\\\\', '\\') # normalize double backslashes

        # Step 3: Try loading as JSON
        return json.loads(json_str)

    except json.JSONDecodeError as e:
        print("JSON decoding failed:", e)
        raise HTTPException(status_code=400, detail=f"Invalid JSON in Gemini response: {str(e)}")
    except Exception as e:
        print("Generic parsing error:", e)
        raise HTTPException(status_code=500, detail=f"Failed to parse Gemini response: {str(e)}")
    
def get_token_from_file():
    with open("token.txt", "r") as f:
        return f.read().strip()


def get_spotify_client():
    token = get_token_from_file()
    return spotipy.Spotify(auth=token)

@app.get("/")
def root():
    return {"message": "Spotify Mood Playlist Creator API"}

@app.get("/login")
def login():
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return {"auth_url": auth_url}

@app.get("/callback")
def callback(request: Request):
    code = request.query_params.get("code")
    sp_oauth = get_spotify_oauth()
    token_info = sp_oauth.get_access_token(code)

    # Optional: Save token_info somewhere (e.g., local file, DB)
    with open("token.txt", "w") as f:
        f.write(token_info["access_token"])

    return RedirectResponse(url="/docs")


@app.get("/get_user_playlists")
def get_user_playlists():
    with open("token.txt", "r") as f:
        access_token = f.read()
    sp = spotipy.Spotify(auth=access_token)

    playlists = sp.current_user_playlists()
    user_info = sp.current_user()
    result = {
        "id": user_info["id"],          
        "display_name": user_info["display_name"],
        "playlists": []
    }

    while playlists:
        for item in playlists["items"]:
            playlist_id = item["id"]
            playlist_name = item["name"]

            result["playlists"].append({
                "id": playlist_id,
                "name": playlist_name,
                "url": item["external_urls"]["spotify"]
            })

        if playlists["next"]:
            playlists = sp.next(playlists)
        else:
            break

    return result



@app.get("/classify_songs_from_playlists")
async def classify_songs_from_playlists(
    playlist_ids: List[str] = Query(...),
    mood: str = Query(...),
    playlist_name: str = Query("Custom Playlist")
):
    all_songs = []

    with open("token.txt", "r") as f:
        access_token = f.read()
    sp = spotipy.Spotify(auth=access_token)


    for pid in playlist_ids:
        tracks = get_playlist_tracks(sp, pid)  
        all_songs.extend(tracks)

    classification_result = classify_songs_by_mood(playlist_name, mood, all_songs)
    return format_gemini_response(classification_result)
    
    


@app.post("/create_mood_playlist_gemini")
async def create_mood_playlist_gemini(
    playlist_ids: List[str] = Query(...),
    mood: str = Query(...),
    playlist_name: str = Query(...),
    user_id: str = Query(...)
):
    token = get_token_from_file()
    sp = spotipy.Spotify(auth=token)

    all_songs = []
    for pid in playlist_ids:
        tracks = get_playlist_tracks(sp, pid)
        all_songs.extend(tracks)

    if not all_songs:
        raise HTTPException(status_code=404, detail="No tracks found in the given playlists.")

    final_formatted = []
    failed_batches = []

    BATCH_SIZE = 80
    DELAY_BETWEEN_REQUESTS = 0.5

    for i in range(0, len(all_songs), BATCH_SIZE):
        
        batch = all_songs[i:i + BATCH_SIZE]
        batch_index = i // BATCH_SIZE + 1
        print(f"Processing batch {batch_index} with {len(batch)} songs")

        try:
            gemini_response = classify_songs_by_mood(playlist_name, mood, batch)
            print(f"Gemini response for batch {batch_index}: {gemini_response}")
            formatted = format_gemini_response(gemini_response)
            final_formatted.extend(formatted)
        except Exception as e:
            failed_batches.append({
                "batch_index": batch_index,
                "error": str(e),
                "failed_songs": batch
            })

        await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

    matching_track_ids = [
        song["spotify_id"]
        for song in final_formatted
        if song and song.get("mood_match", False)
    ]

    playlist_url = None
    if matching_track_ids:
        playlist_url = create_playlist_and_add_tracks(sp, user_id, playlist_name, matching_track_ids)

    return {
        "message": f"Playlist '{playlist_name}' created with {len(matching_track_ids)} tracks matching mood '{mood}'." if matching_track_ids else "No tracks matched the selected mood.",
        "tracks_added": len(matching_track_ids),
        "playlist_url": playlist_url,
        "failed_batches": failed_batches
    }


@app.get("/hello_response")
def hello_response():
    return hello_model()  

@app.post("/create_mood_playlist_gemini_id_only")
async def create_mood_playlist_gemini_idonly(
    playlist_ids: List[str] = Query(...),
    mood: str = Query(...),
    playlist_name: str = Query(...),
    user_id: str = Query(...)
):
    token = get_token_from_file()
    sp = spotipy.Spotify(auth=token)

    all_songs = []
    for pid in playlist_ids:
        tracks = get_playlist_tracks(sp, pid)
        all_songs.extend(tracks)

    if not all_songs:
        raise HTTPException(status_code=404, detail="No tracks found in the given playlists.")

    final_matches = []
    failed_batches = []

    BATCH_SIZE = 80
    DELAY_BETWEEN_REQUESTS = 0.5

    for i in range(0, len(all_songs), BATCH_SIZE):
        batch = all_songs[i:i + BATCH_SIZE]
        batch_index = i // BATCH_SIZE + 1
        print(f"Processing batch {batch_index} with {len(batch)} songs")

        try:
            gemini_response = classify_song_ids_by_mood(playlist_name, mood, batch)

            if isinstance(gemini_response, str):
                # If it's a raw string, attempt to parse
                parsed = format_gemini_response(gemini_response)
            else:
                parsed = gemini_response

            final_matches.extend([
                item["spotify_id"]
                for item in parsed
                if item.get("mood_match") is True
            ])
        except Exception as e:
            failed_batches.append({
                "batch_index": batch_index,
                "error": str(e),
                "failed_songs": batch
            })

        await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

    playlist_url = None
    if final_matches:
        playlist_url = create_playlist_and_add_tracks(sp, user_id, playlist_name, final_matches)

    return {
        "message": f"Playlist '{playlist_name}' created with {len(final_matches)} tracks matching mood '{mood}'." if final_matches else "No tracks matched the selected mood.",
        "tracks_added": len(final_matches),
        "playlist_url": playlist_url,
        "failed_batches": failed_batches
    }