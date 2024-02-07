import sys
import subprocess  # Import the subprocess module
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout, QLabel, QPushButton, QScrollArea, QMessageBox
import os
import shutil 
from datetime import datetime
import spotipy
import configparser
import subprocess
from inspo_spotify_playlist import spotify_authenticate, load_config, create_playlist
from inspo_spotify_playlist import read_inspo_file, add_tracks_to_playlist, select_tracks_for_duration, find_included_tracks, find_seed_tracks, get_recommendations_for_segment

class DraggableLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        current_text = self.text()
        new_text = event.mimeData().text()
        if current_text:
            self.setText(f"{current_text}, {new_text}")
        else:
            self.setText(new_text)

    

class PlaylistGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.segment_count = 0  # Keep track of the number of segments
        self.segment_widgets = {}  # Initialize segment widgets storage
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout(self)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.contentWidget = QWidget()
        self.content_layout = QVBoxLayout(self.contentWidget)

        self.playlist_name_edit = QLineEdit()
        self.playlist_name_edit.setPlaceholderText("Enter Playlist Name Here")
        self.main_layout.addWidget(self.playlist_name_edit)

        self.segments_layout = QVBoxLayout()  # Layout to hold all segments
        self.content_layout.addLayout(self.segments_layout)

        self.add_segment_button = QPushButton("Add Segment")
        self.add_segment_button.clicked.connect(self.add_segment)
        self.content_layout.addWidget(self.add_segment_button)

        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self.export_inspo)
        self.content_layout.addWidget(self.done_button)

        self.scrollArea.setWidget(self.contentWidget)
        self.main_layout.addWidget(self.scrollArea)

        # Add a "Create Playlist" button
        self.create_playlist_button = QPushButton("Create Playlist", self)
        self.create_playlist_button.clicked.connect(self.create_spotify_playlist)
        self.main_layout.addWidget(self.create_playlist_button)

        self.setWindowTitle('Spotify Playlist Generator')

        # Load existing data and initialize the initial segments
        self.load_inspo_data_and_initialize_segments()

        

    def load_inspo_data_and_initialize_segments(self):
        inspo_data = self.load_inspo_data()
        self.playlist_name_edit.setText(inspo_data.get('playlist_name', ''))

        # Remove default segments initialization from __init__ and initialize them here
        for segment_name, segment_data in inspo_data.items():
            if segment_name != 'playlist_name':
                self.create_segment_ui(segment_name)
                widgets = self.segment_widgets[segment_name]
                widgets["example_songs_edit"].setText(segment_data.get('example_songs', ''))
                widgets["included_songs_edit"].setText(segment_data.get('included_songs', ''))
                widgets["target_energy_edit"].setText(str(segment_data.get('target_energy', '')))
                widgets["target_tempo_edit"].setText(str(segment_data.get('target_tempo', '')))
                widgets["duration_edit"].setText(str(segment_data.get('duration', '')))


    def create_segment_ui(self, segment_name="New Segment"):
        segment_label = QLabel(f"{segment_name} Segment:")
        self.segments_layout.addWidget(segment_label)

        example_songs_edit = DraggableLineEdit()
        example_songs_edit.setPlaceholderText("Example Songs")
        self.segments_layout.addWidget(example_songs_edit)

        included_songs_edit = DraggableLineEdit()
        included_songs_edit.setPlaceholderText("Included Songs")
        self.segments_layout.addWidget(included_songs_edit)

        target_energy_edit = QLineEdit()
        target_energy_edit.setPlaceholderText("Target Energy (0.0 to 1.0)")
        self.segments_layout.addWidget(target_energy_edit)

        target_tempo_edit = QLineEdit()
        target_tempo_edit.setPlaceholderText("Target Tempo (BPM)")
        self.segments_layout.addWidget(target_tempo_edit)

        duration_edit = QLineEdit()
        duration_edit.setPlaceholderText("Duration (minutes)")
        self.segments_layout.addWidget(duration_edit)

        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.remove_segment(segment_label, example_songs_edit, included_songs_edit, target_energy_edit, target_tempo_edit, duration_edit, remove_button))
        self.segments_layout.addWidget(remove_button)

        self.segment_count += 1  # Increment the count of segments

        self.segment_widgets[segment_name] = {
        "example_songs_edit": example_songs_edit,
        "included_songs_edit": included_songs_edit,
        "target_energy_edit": target_energy_edit,
        "target_tempo_edit": target_tempo_edit,
        "duration_edit": duration_edit
    }
    def run_inspo_script(self):
        try:
            # Adjust the path to inspo_spotify_playlist.py as necessary
            subprocess.run(["python", "inspo_spotify_playlist.py"], check=True)
            print("Playlist created successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while creating playlist: {e}")

    def add_segment(self):
        segment_name = f"Segment {self.segment_count + 1}"
        self.create_segment_ui(segment_name)

    def remove_segment(self, *widgets):
        for widget in widgets:
            widget.deleteLater()  # Remove the widget
        del self.segment_widgets[segment_name]  # Remove the segment from the dictionary
        self.segment_count -= 1  # Decrement the count of segments

    def export_inspo(self):
        playlist_name = self.playlist_name_edit.text().strip() or "Untitled_Playlist"
        original_filepath = os.path.join(os.getcwd(), 'inspo.txt')  # Path to the original inspo.txt
        archive_dir = os.path.join(os.getcwd(), 'inspo_archive')  # Path to the archive directory

        # Archive the original inspo.txt if it exists
        if os.path.exists(original_filepath):
            # Make sure the archive directory exists
            if not os.path.exists(archive_dir):
                os.makedirs(archive_dir)

            # Create a unique name for the archived file
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            archived_filename = f"inspo-{playlist_name.replace(' ', '_')}-{timestamp}.txt"
            archived_filepath = os.path.join(archive_dir, archived_filename)

            # Move the original inspo.txt to the archive directory
            shutil.move(original_filepath, archived_filepath)
            print(f"Archived original inspo.txt to {archived_filepath}")

        # Write the new information to inspo.txt
        with open(original_filepath, 'w') as file:
            file.write(f"Playlist Name: {playlist_name}\n\n")
            # Write the rest of the information for each segment
            for segment_name, widgets in self.segment_widgets.items():
                example_songs = widgets["example_songs_edit"].text() or "None"
                included_songs = widgets["included_songs_edit"].text() or "None"
                target_energy = widgets["target_energy_edit"].text() or "None"
                target_tempo = widgets["target_tempo_edit"].text() or "None"
                duration = widgets["duration_edit"].text() or "None"
                file.write(f"Name: {segment_name}\nExample Songs: {example_songs}\nIncluded Songs: {included_songs}\nTarget Attributes: target_energy={target_energy}, target_tempo={target_tempo}\nDuration: {duration}\n\n")

        print("Updated inspo.txt with new information.")
        # Show a confirmation message box
        QMessageBox.information(self, "Export Complete", "Your new parameters have been updated successfully!.", QMessageBox.Ok)
   
    def create_spotify_playlist(self):
        # This method is triggered when the "Create Playlist" button is clicked
        try:
            client_id, client_secret, redirect_uri = load_config()
            sp = spotify_authenticate(client_id, client_secret, redirect_uri)
            
            # Read the inspo file and extract playlist name and segments
            file_path = 'inspo.txt'
            playlist_name, segments = read_inspo_file(file_path)

            # Create the playlist
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

        except Exception as e:
            print(f"An error occurred: {e}")


    def load_inspo_data(self, filepath='inspo.txt'):
        data = {}
        try:
            with open(filepath, 'r') as file:
                lines = file.readlines()
            
            current_segment = None
            for line in lines:
                line = line.strip()
                if line.startswith("Playlist Name:"):
                    data['playlist_name'] = line.split(":", 1)[1].strip()
                elif line.startswith("Name:"):
                    current_segment = line.split(":", 1)[1].strip()
                    data[current_segment] = {'example_songs': '', 'included_songs': '', 'target_energy': '', 'target_tempo': '', 'duration': ''}
                elif line.startswith("Example Songs:"):
                    if current_segment:
                        data[current_segment]['example_songs'] = line.split(":", 1)[1].strip()
                elif line.startswith("Included Songs:"):
                    if current_segment:
                        data[current_segment]['included_songs'] = line.split(":", 1)[1].strip()
                elif line.startswith("Target Attributes:"):
                    if current_segment:
                        attrs = line.split(":", 1)[1].strip().split(", ")
                        for attr in attrs:
                            key, value = attr.split("=")
                            data[current_segment][key.strip()] = value.strip()
                elif line.startswith("Duration:"):
                    if current_segment:
                        data[current_segment]['duration'] = line.split(":", 1)[1].strip()
        except FileNotFoundError:
            print(f"No existing {filepath} found. Starting with empty fields.")
    
        return data



def main():
    app = QApplication(sys.argv)
    ex = PlaylistGeneratorApp()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
