# Makefile for SpotifyPlaylist project

# Define the Python command
PYTHON = python3

# Define the pip command for installing Python packages
PIP = pip3

# Target for setting up the project environment
setup:
    @echo "Installing required Python packages..."
    $(PIP) install spotipy==2.23.0 pandas==1.2.4

# Target for creating the config.ini file
config:
    @echo "Creating config.ini..."
    $(PYTHON) create_config.py

# Target for creating the spotify playlist using the gui
create:
    @echo "Running the Spotify Playlist script..."
    $(PYTHON) inspo_gui.py

# Target for cleaning up sensitive information from config.ini
clean:
    @echo "Cleaning config.ini..."
    # This command will remove the config.ini file. If you prefer to just remove sensitive info, you will need a more complex command here.
    rm -f config.ini

# Default target
all: setup create-config run

# Phony targets
.PHONY: setup create-config run clean all
