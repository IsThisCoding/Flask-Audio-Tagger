#!/bin/python

from __future__ import print_function
import os
import acoustid
import music_tag
from musixmatch import Musixmatch
import musicbrainzngs
import requests

# Directory containing the audio files
directory = './static/uploads/'
# AcoustID API key
apikey = '12UBrbecLI'
musixmatch = Musixmatch('7831bcd6fcd67dd40c2b4e712ec8e4b3')

# Set up MusicBrainz user agent
musicbrainzngs.set_useragent("FlaskAudioTagger", "0.1")

def get_lyrics(mbid):
    print(musixmatch.track_lyrics_get(mbid))
    return musixmatch.track_lyrics_get(mbid)

def get_cover_art_url(mbid):
    try:
        # Get the release group for the recording to find the album
        recording = musicbrainzngs.get_recording_by_id(mbid, includes=["releases"])
        release_id = recording['recording']['release-list'][0]['id']
        
        # Fetch cover art from the Cover Art Archive
        cover_art_url = f"http://coverartarchive.org/release/{release_id}/front"
        response = requests.get(cover_art_url)
        
        if response.status_code == 200:
            return cover_art_url
        else:
            return "Cover art not found"
    except musicbrainzngs.ResponseError as e:
        print(f"MusicBrainz error: {e}")
        return None

def download_image(url, save_path):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Open a local file with write-binary mode
            with open(save_path, 'wb') as file:
                # Write the content of the response (the image) to the file
                file.write(response.content)
            print(f"Image successfully downloaded: {save_path}")
        else:
            print(f"Failed to retrieve image. HTTP Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_album_name(recording_id):
    try:
        # Fetch recording details including releases
        data = musicbrainzngs.get_recording_by_id(recording_id, includes=["releases"])
        
        # Check if the recording details are available
        if 'recording' not in data:
            print(f"No recording details found for recording ID '{recording_id}'.")
            return None

        # Get the first non-video release and its details
        recording = data['recording']
        if 'release-list' in recording and recording['release-list']:
            first_release = recording['release-list'][0]
            release_title = first_release['title']
            return release_title
        else:
            print(f"No releases found for recording ID '{recording_id}'.")
            return None
        
    except musicbrainzngs.ResponseError as e:
        print(f"Error fetching recording details for recording ID '{recording_id}': {e}")
        return None

def get_release_year(recording_id):
    try:
        # Fetch recording details including releases
        data = musicbrainzngs.get_recording_by_id(recording_id, includes=["releases"])
        
        # Check if the recording details are available
        if 'recording' not in data:
            print(f"No recording details found for recording ID '{recording_id}'.")
            return None

        # Get the first non-video release and its details
        recording = data['recording']
        if 'release-list' in recording and recording['release-list']:
            first_release = recording['release-list'][0]
            release_date = first_release.get('date', 'N/A')
            if release_date != 'N/A':
                # Extract the year from the release date
                release_year = release_date.split('-')[0]
                return release_year
            else:
                print(f"No release date found for recording ID '{recording_id}'.")
                return None
        else:
            print(f"No releases found for recording ID '{recording_id}'.")
            return None
        
    except musicbrainzngs.ResponseError as e:
        print(f"Error fetching recording details for recording ID '{recording_id}': {e}")
        return None

for filename in os.listdir(directory):
    # Get full path of the file
    path = os.path.join(directory, filename)
    

    f = music_tag.load_file(path)
    
    artist_list = []
    album_list = []
    title_list = []
    rid_list = []
    for score, rid, title, artist in acoustid.match(apikey, path):   
        print(artist)
        artist_list.append(artist)
        title_list.append(title)
        album_list.append(get_album_name(rid))
        rid_list.append(rid)
    print(artist_list)
    print(title_list)
    print(get_lyrics(rid_list[0]))
    img_url = get_cover_art_url(rid_list[0])
    download_image(img_url, './static/artwork/art')

    with open('./static/artwork/art', 'rb') as img_in:
        f['artwork'] = img_in.read()
    
    art = f['artwork']
    art.first.thumbnail([64,64])
    f['artist'] = artist_list[0]
    f['title'] = title_list[0]
    f['album'] = album_list[0]
    f['year'] = get_release_year(rid_list[0])
    f['lyrics'] = musixmatch.matcher_lyrics_get(title_list[0], artist_list[0])['message']

    print(f)
    f.save()


