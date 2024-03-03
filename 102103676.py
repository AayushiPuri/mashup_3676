import sys
import re
import os
from googleapiclient.discovery import build
from pytube import YouTube
from moviepy.editor import AudioFileClip, VideoFileClip, concatenate_audioclips

def convert_videos_to_audio_files():
    print("Converting downloaded videos to audio files...")
    for file in os.listdir():
        if file.endswith(".mp4"):
            video_clip = VideoFileClip(file)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(file.replace(".mp4", ".mp3"))
            video_clip.close()
            audio_clip.close()

def trim_and_rename_audio_files(duration):
    print(f"Trimming and renaming audio files...")

    for file in os.listdir():
        if file.endswith(".mp4"):
            # Generate the new filename
            new_filename = file.replace(".mp4", "_trimmed.mp3")

            # Check if the new filename already exists, add a numerical suffix if needed
            count = 1
            while os.path.exists(new_filename):
                new_filename = file.replace(".mp4", f"_trimmed_{count}.mp3")
                count += 1

            # Trim the video clip and extract audio
            video_clip = VideoFileClip(file).subclip(0, duration)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(new_filename)

            video_clip.close()
            audio_clip.close()

            # Remove the original video file
            os.remove(file)

    print(f"Trimming and renaming completed.")

def search_and_download_videos(api_key, artist_name, num_videos):
    print(f"Searching and downloading {num_videos} videos of {artist_name} from YouTube...")

    youtube_service = initialize_youtube_service(api_key)
    query = f"{artist_name} songs"

    search_results = youtube_service.search().list(
        q=query,
        type='video',
        part='id',
        maxResults=num_videos
    ).execute()

    video_urls = [f"https://www.youtube.com/watch?v={item['id']['videoId']}" for item in search_results['items']]

    for i, video_url in enumerate(video_urls):
        try:
            print(f"Downloading Video {i + 1} - URL: {video_url}")
            YouTube(video_url).streams.get_highest_resolution().download()
        except Exception as e:
            print(f"Error downloading Video {i + 1}: {e}")


def initialize_youtube_service(api_key):
    return build('youtube', 'v3', developerKey=api_key)

def extract_video_id_from_url(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def merge_audio_files(output_filename):
    print("Merging all audio files into a single output file...")
    audio_clips = [AudioFileClip(file) for file in os.listdir() if file.endswith(".mp3")]
    final_audio = concatenate_audioclips(audio_clips)
    final_audio.write_audiofile(output_filename)

def create_music_mashup(api_key, artist_name, num_videos, audio_duration, output_filename):
    try:
        search_and_download_videos(api_key, artist_name, num_videos)
        convert_videos_to_audio_files()
        trim_and_rename_audio_files(audio_duration)
        merge_audio_files(output_filename)
        print(f"Music Mashup completed! Output file: {output_filename}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python 102103345.py artist_name num_videos audio_duration 102103345_output.mp3")
    else:
        _, artist_name, num_videos, audio_duration, output_filename = sys.argv
        num_videos = int(num_videos)
        audio_duration = int(audio_duration)
        create_music_mashup('AIzaSyAzrMmAAgGJygxEkBI96aGVLTekpB_LkcY', artist_name, num_videos, audio_duration, output_filename)
