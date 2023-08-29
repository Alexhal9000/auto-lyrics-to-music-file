import os
import sys
import eyed3
import time
import json
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

# Function to update lyrics metadata of a music file
def update_lyrics(file_path, dalyrics):
    audiofile = eyed3.load(file_path)
    audiofile.tag.lyrics.set(dalyrics)
    audiofile.tag.save(version=(2, 4, 0))  # Save in ID3 v2.3 format

def get_all_songs(artist):

    agent = 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) \
        Gecko/20100101 Firefox/24.0'
    headers = {'User-Agent': agent}
    base = "https://www.azlyrics.com/"

    artist = artist.lower().replace(" ", "")
    first_char = artist[0]
    url = base + first_char + "/" + artist + ".html"
    req = requests.get(url, headers=headers)

    artist = {
        'artist': artist,
        'albums': {}
    }

    soup = BeautifulSoup(req.content, 'html.parser')

    all_albums = soup.find('div', id='listAlbum')
    first_album = all_albums.find('div', class_='album')
    album_name = first_album.b.text

    s = []

    for tag in first_album.find_next_siblings(['a', 'div']):
        if tag.class_ == 'album':
            artist['albums'][album_name] = s
            s = []
            if tag.b is None:
                pass
            elif tag.b:
                album_name = tag.b.text

        else:
            if tag.text == "":
                pass
            else:
                s.append(tag.text)


    artist['albums'][album_name] = s

    return artist

def lyrics(artist, song):

    agent = 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) \
        Gecko/20100101 Firefox/24.0'
    headers = {'User-Agent': agent}
    base = "https://www.azlyrics.com/"

    artist = artist.lower().replace(" ", "")
    song = song.lower().replace(" ", "").replace(".", "").replace(",", "")
    url = base + "lyrics/" + artist + "/" + song + ".html"

    req = requests.get(url, headers=headers)
    soup = BeautifulSoup(req.content, "html.parser")
    l = soup.find_all("div", attrs={"class": None, "id": None})
    if not l:
        return {'Error': 'Unable to find ' + song + ' by ' + artist}
    elif l:
        l = [x.getText() for x in l]
        return l

# Function to find the closest matching song
def find_closest_song(artist, target_title):
    artist_songs = get_all_songs(artist)
    best_match = None
    best_similarity = 0

    for album, songs_list in artist_songs['albums'].items():
        for song in songs_list:
            similarity = fuzz.ratio(song, target_title)
            #print(f"{song}:({similarity})")
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = song

    return best_match


# Function to search for music files and update lyrics metadata
def update_lyrics_for_music_files(root_folder):
    for root, _, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith(('.mp3', '.flac', '.ogg', '.wav', '.m4a', '.aac', '.wma', '.ape', '.alac', '.aiff')):
                file_path = os.path.join(root, file)
                print(f"Processing {file_path}")

                # Load audio metadata
                audiofile = eyed3.load(file_path)
                if audiofile.tag is None:
                    audiofile.initTag()

                # Check if lyrics metadata already exists
                try:
                    if len(audiofile.tag.lyrics[0].text) > 2:
                        #print(audiofile.tag.lyrics[0].text)
                        print("Lyrics already present. Skipping.")
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
                        print(dalyrics[0])
                        if len(dalyrics[0])>2:
                            update_lyrics(file_path, dalyrics[0])
                            print("Lyrics updated successfully.")
                    except Exception as e:
                        print(f"Error: ({str(e)})")
                        if str(e) == "0":
                            print("No exact match found. Trying to find the closest match.")
                            closest_song = find_closest_song(artist_name, song_title)
                            if closest_song:
                                print(f"Closest match found: {closest_song}")
                                song_title = closest_song
                                try:
                                    dalyrics = lyrics(artist_name, song_title)
                                    print(f"{artist_name} - {song_title}")
                                    print(dalyrics[0])
                                    if len(dalyrics[0])>2:
                                        update_lyrics(file_path, dalyrics[0])
                                        print("Lyrics updated successfully.")                                        
                                except Exception as e:
                                    print(f"Error: {str(e)}")
                                    if str(e) == "0":
                                        print("Lyrics not found on AzLyrics.")            
                else:
                    print("Artist and song title metadata not available. Skipping.")

                time.sleep(1)  # Add a 1-second delay

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
