from fastapi import APIRouter, HTTPException
from fastapi import Query
from typing import List
from services.spotify_service import SpotifyService


router = APIRouter()

spotify_service = SpotifyService()


@router.get("/get_user_playlists")
def get_user_playlists():
    try:
        spotify_service.refresh_token()
        return spotify_service.get_user_playlists()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/classify_songs_from_playlists")
async def classify_songs_from_playlists(
        playlist_ids: List[str] = Query(...),
        mood: str = Query(...),
        playlist_name: str = Query("Custom Playlist")
    ):
    
    try:

        if not playlist_ids:
            raise HTTPException(status_code=400, detail="No playlist IDs provided.")
        
        if not mood:
            raise HTTPException(status_code=400, detail="Mood is required.")
        
        if not playlist_name:
            raise HTTPException(status_code=400, detail="Playlist name is required.")
        
        spotify_service.refresh_token()
        classified_songs = await spotify_service.classify_songs_from_playlists(playlist_ids, mood, playlist_name)

        return classified_songs
    
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/create_mood_playlist_gemini_id_only")
async def create_mood_playlist_gemini_idonly(
        playlist_ids: List[str] = Query(...),
        mood: str = Query(...),
        playlist_name: str = Query(...),
        user_id: str = Query(...)
    ):

    try:
        if not playlist_ids:
            raise HTTPException(status_code=400, detail="No playlist IDs provided.")
        
        if not mood:
            raise HTTPException(status_code=400, detail="Mood is required.")
        
        if not playlist_name:
            raise HTTPException(status_code=400, detail="Playlist name is required.")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required.")

        spotify_service.refresh_token()
        playlist_response = await spotify_service.create_mood_playlist(playlist_ids, mood, playlist_name, user_id)

        return {
            "message": f"Playlist '{playlist_name}' created with {playlist_response['tracks_added']} tracks matching mood '{mood}'." if playlist_response['tracks_added'] > 0 else "No tracks matched the selected mood.",
            "tracks_added": playlist_response['tracks_added'],
            "playlist_url": playlist_response.get('playlist_url'),
            "failed_batches": playlist_response.get('failed_batches', [])
        }
    
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))