#!/bin/python

from __future__ import print_function
import os
import acoustid
import music_tag
import musicbrainzngs

# Directory containing the audio files
directory = './static/uploads/'
# AcoustID API key
apikey = '12UBrbecLI'

# Set up MusicBrainz user agent
musicbrainzngs.set_useragent("FlaskAudioTagger", "0.1")

for filename in os.listdir(directory):
    # Get full path of the file
    path = os.path.join(directory, filename)

    non_video = "error"
    try:
        # Perform AcoustID match
        for score, rid, title, artist in acoustid.match(apikey, path):
            # Fetch recording details including releases
            data = musicbrainzngs.get_recording_by_id(rid, includes=["releases"])

            # Check if the recording is a video
            if 'video' in data['recording'] and data['recording']['video']:
                continue  # Skip video recordings

            non_video = data['recording']
            #print(f"Title: {non_video['title']}")
            #print(f"Recording ID: {non_video['id']}")

            # Get the first non-video release and its details
            if 'release-list' in non_video and non_video['release-list']:
                first_release = non_video['release-list'][0]
                release_title = first_release['title']
                release_id = first_release['id']
                release_date = first_release.get('date', 'N/A')
                release_country = first_release.get('country', 'N/A')

                #   print(f"Album (Release) Title: {release_title}")
                #print(f"Release ID: {release_id}")
                #print(f"Release Date: {release_date}")
                #print(f"Release Country: {release_country}")

                # Tag the file using music_tag
                f = music_tag.load_file(path)
                f['title'] = non_video['title']
                #f['artist'] = ', '.join(artist['name'] for artist in non_video['artist-credit'])
                f['album'] = release_title
                f['release_date'] = release_date
                f['country'] = release_country
                print(f)
            break  # Exit after processing the first result

    except Exception as e:
        print(f"Error processing {filename}: {e}")


