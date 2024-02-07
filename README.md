# Create the perfect playlist on Spotify

This application allows you to take full advantage of Spotify's reccomendation features to create
fun and interesting playlists that change up the vibe at intervals of your choosing.

This application was built for yoga teachers who want a faster way to create thoughtful yoga playlists 
without spending all afternoon on Spotify!

It works by creating different segments for each part of the playlist. Each segment gets assigned songs of your choosing to use as inspiration, along with the duration of the segment and other attributes (BPM, energy). This allows you to create the exact vibe you want at intervals meaningful to your class.

## What you need
- Spotify developer API access (see below for more information)
- A song or two in mind that suit each segment of your playlist!

**Baseline segments include the following:**

* Breath: 5 min of slow meditation music, tempo 70, energy 0.2
* Warm-up: 10 min of chill upbeat music, tempo 100, energy 0.4
* Flow 1: 15 min of chill pop music, tempo 130, energy 0.8
* Flow 2: 10 min of upbeat pop music, tempo 130, energy 0.8
* Cooldown: 15 min of calm vibey music, tempo 80, energy 0.4
* Savasana: 10 min of meditation music, tempo 70, energy 0.2

## Features

- Create Spotify playlists automatically.
- GUI for easy interaction.
- Customizable playlist settings.

## Getting Started 
To get started, clone this repository and install the required dependencies:

```
git clone https://github.com/tayloraportman/SpotifyPlaylist.git
cd SpotifyPlaylist
pip install -r requirements.txt
```
### Spotify for Developers
To use this playlist deveolpmet tool you will need to create a spotify for developers app. To do this: 
1. Go to https://developer.spotify.com/ and log in to Spotify
2. Select 'create application' and check the box for 'Web API'
- This will bring you to a page where you can access your personal Client ID and Client Secret
3. Input Client ID and Client Secret into the config settings 
- In terminal run the following command: 
```
make config
```
- This will prompt you to enter your Client ID and Client Secret
- If you need to change the Client ID and or Client Secret, or it was entered incorrectly, you can reset the cofig settings by running 'make clean' and start again

## Create your playlist!
To create your playlist run the following command:
```
make create
```
This will open up an interface where you can name your playlist, add songs to inspire each segment of the playlist, and edit the segments to your needs. 

Each segment includes a window to input: 
- Example Songs (used to inspire the Spotify's reccommendation feature)
- Songs you want to include
- Target tempo (BPM)
- Target energy (0.0-1)
- Segment duration (minutes)

### When you have finished modifying the segments and want to save your settings scroll down and select the 'done' button
This will save the old playlist inspo to an inspo_archive folder and update the playlist settings

### When you are ready to create your playlist select 'create playlist' and check out your sweet new playlist on Spotify!

## License

- MIT License, see the LICENSE file for more information

## Author
Taylor A. Portman
* With help from Chat GPT 4

## Version
- Version 1.0, Feburary 7, 2024








