def create_inspo_file():
    playlist_name = input("Enter the playlist name: ")

    # Predefined segment details
    segments_info = [
        {"name": "Breath", "target_attributes": "target_energy=0.2, target_tempo=70", "duration": "5"},
        {"name": "Warm-up", "target_attributes": "target_energy=0.4, target_tempo=100", "duration": "10"},
        {"name": "Flow 1", "target_attributes": "target_energy=0.8, target_tempo=130", "duration": "15"},
        {"name": "Flow 2", "target_attributes": "target_energy=0.8, target_tempo=130", "duration": "10"},
        {"name": "Cool down", "target_attributes": "target_energy=0.4, target_tempo=80", "duration": "15"},
        {"name": "Savasana", "target_attributes": "target_energy=0.2, target_tempo=70", "duration": "10"}
    ]

    segments = []
    for segment_info in segments_info:
        print(f"\nEntering details for segment: {segment_info['name']}")
        example_songs = input("Example songs (comma-separated): ")
        included_songs = input("Included songs (comma-separated, type 'none' if there are none): ")

        segments.append({
            'name': segment_info['name'],
            'example_songs': example_songs,
            'included_songs': included_songs,
            'target_attributes': segment_info['target_attributes'],
            'duration': segment_info['duration']
        })

    with open('inspo.txt', 'w') as file:
        file.write(f"Playlist Name: {playlist_name}\n\n")
        for segment in segments:
            file.write(f"Name: {segment['name']}\n")
            file.write(f"Example Songs: {segment['example_songs']}\n")
            file.write(f"Included Songs: {segment['included_songs']}\n")
            file.write(f"Target Attributes: {segment['target_attributes']}\n")
            file.write(f"Duration: {segment['duration']}\n\n")

    print("inspo.txt file has been created successfully.")

if __name__ == '__main__':
    create_inspo_file()
