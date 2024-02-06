import spotipy
from spotipy.oauth2 import SpotifyOAuth
import configparser

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['SPOTIFY']['CLIENT_ID'], config['SPOTIFY']['CLIENT_SECRET'], config['SPOTIFY']['REDIRECT_URI']

client_id, client_secret, redirect_uri = load_config()


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

def find_included_tracks(sp, included_songs):
    included_track_ids = []
    for song in included_songs:
        results = sp.search(q=song, limit=1, type='track')
        tracks = results['tracks']['items']
        if tracks:
            included_track_ids.append(tracks[0]['id'])
    return included_track_ids

def select_tracks_for_duration(tracks, target_duration_minutes):
    selected_tracks = []
    total_duration_ms = 0
    target_duration_ms = target_duration_minutes * 60 * 1000  # Convert minutes to milliseconds

    for track in tracks:
        track_duration_ms = track['duration_ms']
        if total_duration_ms + track_duration_ms <= target_duration_ms:
            selected_tracks.append(track['id'])
            total_duration_ms += track_duration_ms
        else:
            break  # Stop adding tracks once the target duration is reached or exceeded

    return selected_tracks

def main():
    client_id, client_secret, redirect_uri = load_config()

    sp = spotify_authenticate(client_id, client_secret, redirect_uri)

    # Read and parse the inspo.txt file
    playlist_name, segments = read_inspo_file('inspo.txt')  

    # Create a playlist with the parsed name
    playlist_id = create_playlist(sp, playlist_name)

    for segment in segments:
        # Find seed tracks and get recommendations
        seed_track_ids = find_seed_tracks(sp, segment['example_songs'])
        recommended_tracks = get_recommendations_for_segment(sp, seed_track_ids, segment['target_attributes'], limit=50)  # Increase limit if needed
        recommended_track_ids = [track['id'] for track in recommended_tracks]

        # Find included tracks
        included_track_ids = find_included_tracks(sp, segment.get('included_songs', []))

        # Combine recommended and included tracks and fetch their details
        all_tracks = sp.tracks(recommended_track_ids + included_track_ids)['tracks']

        # Filter out explicit tracks
        non_explicit_tracks = [track for track in all_tracks if not track['explicit']]

        # Select tracks based on duration from non-explicit tracks
        selected_track_ids = select_tracks_for_duration(non_explicit_tracks, float(segment['duration']))

        # Add selected tracks to the playlist
        add_tracks_to_playlist(sp, playlist_id, selected_track_ids)



def read_inspo_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    playlist_name_line = lines[0].strip()
    playlist_name_prefix = "Playlist Name:"
    if playlist_name_line.startswith(playlist_name_prefix):
        playlist_name = playlist_name_line[len(playlist_name_prefix):].strip()
    else:
        raise ValueError("The first line must start with 'Playlist Name:'")

    segments = []
    current_segment = {}

    for line in lines[1:]:  # Skip the first line (playlist name)
        if line.strip() == "":  # Empty line indicates a new segment
            if current_segment:  # If the current segment is not empty, add it to the segments list
                segments.append(current_segment)
                current_segment = {}  # Reset for the next segment
        else:
            key, value = line.split(':', 1)  # Split each line into key and value by the first colon
            key = key.strip().lower()
            value = value.strip()

            if value.lower() == 'none':  # Check for 'None' placeholder
                value = []

            if key in ['name', 'duration']:
                current_segment[key] = value
            elif key == 'example songs':
                current_segment['example_songs'] = [song.strip() for song in value.split(',')] if value else []
            elif key == 'included songs':
                current_segment['included_songs'] = [song.strip() for song in value.split(',')] if value else []
            elif key == 'target attributes':
                attributes = {}
                if value:  # Ensure there are target attributes to process
                    for attr in value.split(','):
                        attr_key, attr_value = attr.split('=')
                        attributes[attr_key.strip()] = float(attr_value.strip())
                current_segment['target_attributes'] = attributes

    if current_segment:  # Add the last segment if the file doesn't end with an empty line
        segments.append(current_segment)

    return playlist_name, segments




if __name__ == '__main__':
    main()
