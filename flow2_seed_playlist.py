import spotipy
from spotipy.oauth2 import SpotifyOAuth

def spotify_authenticate(client_id, client_secret, redirect_uri):
    scope = 'playlist-modify-public'
    auth_manager = SpotifyOAuth(client_id=client_id,
                                client_secret=client_secret,
                                redirect_uri=redirect_uri,
                                scope=scope)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp

def create_playlist(sp, name, description=""):
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user=user_id, name=name, public=True, description=description)
    return playlist['id']

def add_tracks_to_playlist(sp, playlist_id, track_ids):
    sp.playlist_add_items(playlist_id=playlist_id, items=track_ids)

def create_numbered_playlist(sp, base_name, count):
    playlist_name = f"{base_name}#{count}"  # Use string formatting to include the count
    playlist_id = create_playlist(sp, playlist_name)  # Create the playlist with the dynamically generated name
    return playlist_id

def get_recommendations_for_segment(sp, seed_tracks, target_attributes, limit=10):
    recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=limit, **target_attributes)
    return recommendations['tracks']

def find_seed_tracks(sp, example_songs):
    seed_track_ids = []
    for song in example_songs:
        results = sp.search(q=song, limit=1, type='track')
        tracks = results['tracks']['items']
        if tracks:
            seed_track_ids.append(tracks[0]['id'])
    return seed_track_ids

def select_tracks_for_duration(tracks, target_duration_minutes):
    selected_tracks = []
    total_duration_ms = 0
    target_duration_ms = target_duration_minutes * 60 * 1000

    for track in tracks:
        if total_duration_ms + track['duration_ms'] <= target_duration_ms:
            selected_tracks.append(track['id'])
            total_duration_ms += track['duration_ms']
        else:
            break

    return selected_tracks

def main():
    client_id = '94518329d8104cb7aa4420580670e6d3'
    client_secret = '2a1ee85c5d3d469da9a9883bd1f225c5'
    redirect_uri = 'http://localhost:8888/callback'

    sp = spotify_authenticate(client_id, client_secret, redirect_uri)

    # Define segments with example songs, target attributes, and durations
    segments = [
        {
            "name": "Breath",
            "example_songs": ["Now & Anatma - Breathe In Life", "Studio Tranquilo - Serenity"],
            "target_attributes": {"target_energy": 0.2, "target_tempo": 70},
            "duration": 5
        },
        {
            "name": "Warm-up",
            "example_songs": ["Beauvois - Echo", "FACESOUL - Love", "Mac Miller - Good News", "whatever mike - Word to the Trees", "ODEZA - Kusanagi"],
            "target_attributes": {"target_energy": 0.4, "target_tempo": 100},
            "duration": 10
        },
        {
            "name": "Flow 1",
            "example_songs": ["Katie Tupper - Little Love", "Lily Meola - Sunshine", ],
            "target_attributes": {"target_energy": 0.8, "target_tempo": 130},
            "duration": 15
        },
        {
            "name": "Flow 2",
            "example_songs": ["ODIE - Little Lies", "Trevor Hall - Blue Mountain State"],
            "target_attributes": {"target_energy": 0.8, "target_tempo": 130},
            "duration": 10
        },
        {
            "name": "Cool down",
            "example_songs": ["Beautiful Chorus - Success", "Chris Sholar - Let Go"],
            "target_attributes": {"target_energy": 0.4, "target_tempo": 80},
            "duration": 15
        },
        {
            "name": "Savasana",
            "example_songs": ["Steven Halpern - Tibetan Bowl I", "Steven Halpern - Deep Theta 4 Hz"],
            "target_attributes": {"target_energy": 0.2, "target_tempo": 70},
            "duration": 10
        },
        # Add other segments...
    ]

    # Initialize a counter for the playlist number
    playlist_count = 4

    # Create a numbered playlist
    playlist_id = create_numbered_playlist(sp, "60 min Flow2-Python", playlist_count)

    for segment in segments:
        seed_track_ids = find_seed_tracks(sp, segment["example_songs"])
        if seed_track_ids:
            recommendations = get_recommendations_for_segment(sp, seed_track_ids, segment["target_attributes"], limit=20)
            # Select tracks for the segment, ensuring the total duration meets the segment's requirement
            selected_track_ids = select_tracks_for_segment_duration(recommendations, segment["duration"])
            # Add selected tracks to the playlist
            add_tracks_to_playlist(sp, playlist_id, selected_track_ids)

    print(f"Created playlist with ID: {playlist_id}")

def select_tracks_for_segment_duration(tracks, target_duration_minutes):
    selected_tracks = []
    total_duration_ms = 0
    target_duration_ms = target_duration_minutes * 60 * 1000

    for track in tracks:
        # Skip explicit tracks
        if track['explicit']:
            continue

        if total_duration_ms + track['duration_ms'] < target_duration_ms:
            selected_tracks.append(track['id'])
            total_duration_ms += track['duration_ms']
        # Optionally add the last track even if it slightly exceeds the target duration
        elif not selected_tracks:  # If no tracks have been added yet
            selected_tracks.append(track['id'])
            break

    return selected_tracks

if __name__ == '__main__':
    main()
