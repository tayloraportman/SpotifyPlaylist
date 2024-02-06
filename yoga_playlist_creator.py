import spotipy
from spotipy.oauth2 import SpotifyOAuth
#----------------------------------------------------------------
#Authenticate Spotify with credentials
def spotify_authenticate(client_id, client_secret, redirect_uri):
    scope = 'playlist-modify-public'
    auth_manager = SpotifyOAuth(client_id=client_id,
                                client_secret=client_secret,
                                redirect_uri=redirect_uri,
                                scope=scope)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp
#-----------------------------------------------------------------
# Function to search and select tracks based on target duration and vibe
def search_and_select_tracks(sp, vibe, target_duration_minutes):
    tracks = search_tracks(sp, keyword=vibe, limit=50)  # Adjust limit as needed
    selected_tracks = []
    total_duration_ms = 0
    target_duration_ms = target_duration_minutes * 60 * 1000

    for track in tracks:
        if total_duration_ms + track[2] <= target_duration_ms:
            selected_tracks.append(track[1])  # track[1] is the track ID
            total_duration_ms += track[2]

    return selected_tracks

# Segment definitions
segments = [
    {"breath": "breath", "duration": 10},
    {"warmup": "chill vibes", "duration": 5},
    {"flow1": "pop vibes", "duration": 10},
    {"flow2": "vibey keyword", "duration": 10},
    {"cooldown": "chill keyword", "duration": 10},
    {"savasana": "meditation keyword", "duration": 5}
]

# Search for and select tracks for each segment
playlist_tracks = []
for segment in segments:
    segment_tracks = search_and_select_tracks(sp, segment["vibe"], segment["duration"])
    playlist_tracks.extend(segment_tracks)
def search_tracks(sp, keyword, limit=10):
    results = sp.search(q=keyword, limit=limit, type='track')
    tracks = results['tracks']['items']
    return [(track['name'], track['id'], track['duration_ms']) for track in tracks]

def create_playlist(sp, name, description=""):
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user=user_id, name=name, public=True, description=description)
    return playlist['id']

def add_tracks_to_playlist(sp, playlist_id, track_ids):
    sp.playlist_add_items(playlist_id=playlist_id, items=track_ids)

def main():
    client_id = '94518329d8104cb7aa4420580670e6d3'
    client_secret = '2a1ee85c5d3d469da9a9883bd1f225c5'
    redirect_uri = 'http://localhost:8888/callback'

    sp = spotify_authenticate(client_id, client_secret, redirect_uri)

    keyword = "yoga"
    tracks = search_tracks(sp, keyword, 20)

    # Assuming each yoga session track is approximately 3-5 minutes, select enough tracks to fill 60 minutes
    selected_tracks = []
    total_duration_ms = 0
    for name, track_id, duration_ms in tracks:
        if total_duration_ms < 3600000:  # 60 minutes in milliseconds
            selected_tracks.append(track_id)
            total_duration_ms += duration_ms

    playlist_id = create_playlist(sp, "60 Minute Yoga Session-Trial#1")
    add_tracks_to_playlist(sp, playlist_id, selected_tracks)

    print(f"Playlist created with ID: {playlist_id}")

if __name__ == '__main__':
    main()
