import os
import sys
import eyed3
import time
import json
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from unidecode import unidecode
import random
import re
from musixmatch import Musixmatch

# Initialize the Musixmatch API client with your API key
API_KEY = "yourapikey"
# Create an instance with your API key
musixmatch = Musixmatch(API_KEY)

# Function to update lyrics metadata of a music file
def update_lyrics(file_path, dalyrics):
    audiofile = eyed3.load(file_path)
    audiofile.tag.lyrics.set(dalyrics)
    audiofile.tag.save(version=(2, 3, 0))  # Save in ID3 v2.3 format

def replace_special_characters(input_string):
    # Special replacements
    normalized_string = input_string.replace("ï", "")

    # Transliterate the input string into ASCII characters
    normalized_string = unidecode(normalized_string)

    # Remove characters that are outside the range of letters and numbers
    normalized_string = re.sub(r'[^a-zA-Z0-9]+', '', normalized_string).lower()
    
    return normalized_string


# Function to fetch lyrics using the Musixmatch API
def lyrics(artist, song):
    try:
        
        # Search for the track by artist and song name
        track = musixmatch.track_search(q_track=song, q_artist=artist, page_size=1, page=1, s_track_rating='desc')
    
        track_id = track["message"]["body"]["track_list"][0]["track"]["track_id"]

        # Get the lyrics
        lyrics = musixmatch.track_lyrics_get(track_id)

        # Print the lyrics body
        # print(lyrics["message"]["body"]["lyrics"]["lyrics_body"])

        if len(lyrics["message"]["body"]["lyrics"]["lyrics_body"]) > 2:
            return lyrics["message"]["body"]["lyrics"]["lyrics_body"]
        else:
            return None
    except Exception as e:
        return None



# Function to search for music files and update lyrics metadata
def update_lyrics_for_music_files(root_folder):
    for root, _, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith(('.mp3', '.flac', '.ogg', '.wav', '.m4a', '.aac', '.wma', '.ape', '.alac', '.aiff')):
                file_path = os.path.join(root, file)
                #print(f"Processing {file_path}")

                # Load audio metadata
                audiofile = eyed3.load(file_path)
                if audiofile.tag is None:
                    audiofile.initTag()

                # Check if lyrics metadata already exists
                try:
                    if len(audiofile.tag.lyrics[0].text) > 4:
                        #print(audiofile.tag.lyrics[0].text)
                        #print("Lyrics already present. Skipping.")
                        continue
                except Exception as e:
                    print("Lyrics required for:")
  
                # Fetch lyrics from AzLyrics
                artist_name = audiofile.tag.artist
                song_title = audiofile.tag.title

                if artist_name and song_title:
                    try:
                        dalyrics = lyrics(artist_name, song_title)
                        print(f"{artist_name} - {song_title}")
                        #print(dalyrics)
                        if len(dalyrics)>2:
                            update_lyrics(file_path, dalyrics)
                            print("Lyrics updated successfully.")
                    except Exception as e:
                        print(f"Error: ({str(e)})")
                        print("Lyrics not found on Musixmatch.")            
                else:
                    print(f"Artist and song title metadata not available. Skipping: {file_path}")

                time.sleep(1)  # Add a random-seconds delay

# Main function
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python find_lyrics.py <folder>")
        sys.exit(1)

    target_folder = sys.argv[1]
    if not os.path.exists(target_folder):
        print("Folder not found.")
        sys.exit(1)

    update_lyrics_for_music_files(target_folder)