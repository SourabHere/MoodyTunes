import time

def escape_for_prompt(s: str):
    return s.replace("\\", "\\\\").replace("\"", "\\\"")


def get_all_tracks_from_playlists(sp, playlist_ids):
    track_ids = []
    for pid in playlist_ids:
        results = sp.playlist_tracks(pid)
        while results:
            for item in results['items']:
                track = item['track']
                if track:
                    track_ids.append(track['id'])
            if results['next']:
                results = sp.next(results)
            else:
                break
    return track_ids

def create_playlist_and_add_tracks(sp, user_id, playlist_name, track_ids):
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
    playlist_id = playlist["id"]

    for i in range(0, len(track_ids), 5): 
        batch = track_ids[i:i + 5]
        print(f"Adding tracks {i+1} to {i+len(batch)} to playlist {playlist_name} ({playlist_id})")
        print(batch) 
        sp.playlist_add_items(playlist_id, batch)
        print(f"Added tracks {i+1} to {i+len(batch)}")
        time.sleep(0.3)  

    return playlist["external_urls"]["spotify"]


def get_playlist_tracks(sp, playlist_id):
    results = []
    offset = 0

    while True:
        response = sp.playlist_items(playlist_id, offset=offset, fields='items(track(name, artists(name), id, external_urls(spotify))),next')
        
        for item in response['items']:
            track = item['track']
            if not track:
                continue
            results.append({
                "artist_name": escape_for_prompt(track["artists"][0]["name"]) if "artists" in track else "Unknown Artist",
                "song_name": escape_for_prompt(track["name"]),
                "spotify_url": track["external_urls"]["spotify"],
                "spotify_id": track["id"]
            })

        if response['next']:
            offset += len(response['items'])
        else:
            break

    return results