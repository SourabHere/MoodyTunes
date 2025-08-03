import asyncio
from fastapi import HTTPException
import spotipy
from utils.playlist_utils import create_playlist_and_add_tracks, get_playlist_tracks
from services.LLM_factory import LLMFactory


class SpotifyService:
    def __init__(self, token_path="token.txt"):

        with open(token_path, "r") as f:
            self.access_token = f.read().strip()
        
        self.sp = spotipy.Spotify(auth=self.access_token)

    
    def get_user_playlists(self):
        playlists = self.sp.current_user_playlists()
        user_info = self.sp.current_user()
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
                playlists = self.sp.next(playlists)
            else:
                break

        return result
    

    async def classify_songs_from_playlists(self, playlist_ids, mood, playlist_name, LLM="gemini"):
        
        all_songs = []

        for pid in playlist_ids:
            tracks = get_playlist_tracks(self.sp, pid)
            all_songs.extend(tracks)

        llm_model = LLMFactory.get_llm(LLM)
        filtered_songs = []
        failed_batches = []

        BATCH_SIZE = 80
        DELAY_BETWEEN_REQUESTS = 0.5

        for i in range(0, len(all_songs), BATCH_SIZE):
            batch = all_songs[i:i + BATCH_SIZE]
            
            try:
                print(f"[Batch {i+1}/{len(batch)}] Sending {len(batch)} songs")
                result = llm_model.classify_songs_by_mood(playlist_name, mood, batch)
                filtered_songs.append(result)
            except Exception as e:
                print(f"❌ Failed to process batch {i+1}: {e}")
                failed_batches.append({
                    "batch_index": i // BATCH_SIZE + 1,
                    "error": str(e),
                    "failed_songs": batch
                })
                continue  # Skip this batch, proceed with next
            await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

        return {
            "playlist_name": playlist_name,
            "filtered_songs": filtered_songs,
            "failed_batches": failed_batches
        }
    


    async def create_mood_playlist(self, playlist_ids, mood, playlist_name, user_id, LLM="gemini"):
        all_songs = []
        for pid in playlist_ids:
            tracks = get_playlist_tracks(self.sp, pid)
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
                gemini_response = LLMFactory.get_llm(LLM).classify_song_ids_by_mood(playlist_name, mood, batch)


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
            playlist_url = create_playlist_and_add_tracks(self.sp, user_id, playlist_name, final_matches)

        return {
            "tracks_added": len(final_matches),
            "playlist_url": playlist_url,
            "failed_batches": failed_batches
        }

