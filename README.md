# auto-lyrics-to-music-file
This Python script looks up the lyrics from Azlyrics for all song files in a folder. Then it fetches them and writes them into the metadata ID3 tags. 

For Azlyrics and Musixmatch. Bare in mind that Azlyrics does not have an API service and will get you blocked if many requests are made.

## Usage

```bash
python find_lyrics.py <folder or subfolders with songs>
python find_lyrics_musixmatch.py <folder or subfolders with songs>
```

