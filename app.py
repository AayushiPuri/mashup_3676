import streamlit as st
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from moviepy.editor import VideoFileClip, concatenate_audioclips, AudioFileClip
from pytube import YouTube
from googleapiclient.discovery import build


def convert_videos_to_audio_files():
    st.write("Converting downloaded videos to audio files...")
    for file in os.listdir():
        if file.endswith(".mp4"):
            video_clip = VideoFileClip(file)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(file.replace(".mp4", ".mp3"))
            video_clip.close()
            audio_clip.close()


def trim_and_rename_audio_files(duration):
    st.write(f"Trimming and renaming audio files...")

    for file in os.listdir():
        if file.endswith(".mp4"):
            new_filename = file.replace(".mp4", "_trimmed.mp3")
            count = 1
            while os.path.exists(new_filename):
                new_filename = file.replace(".mp4", f"_trimmed_{count}.mp3")
                count += 1
            video_clip = VideoFileClip(file).subclip(0, duration)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(new_filename)
            video_clip.close()
            audio_clip.close()
            os.remove(file)

    st.write(f"Trimming and renaming completed.")


def search_and_download_videos(api_key, artist_name, num_videos):
    st.write(f"Searching and downloading {num_videos} videos of {artist_name} from YouTube...")

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
            st.write(f"Downloading Video {i + 1} - URL: {video_url}")
            YouTube(video_url).streams.get_highest_resolution().download()
        except Exception as e:
            st.write(f"Error downloading Video {i + 1}: {e}")


def initialize_youtube_service(api_key):
    return build('youtube', 'v3', developerKey=api_key)


def merge_audio_files(output_filename):
    st.write("Merging all audio files into a single output file...")
    audio_clips = [AudioFileClip(file) for file in os.listdir() if file.endswith(".mp3")]
    final_audio = concatenate_audioclips(audio_clips)
    final_audio.write_audiofile(output_filename)


def create_music_mashup(api_key, artist_name, num_videos, audio_duration, output_filename):
    try:
        search_and_download_videos(api_key, artist_name, num_videos)
        convert_videos_to_audio_files()
        trim_and_rename_audio_files(audio_duration)
        merge_audio_files(output_filename)
        st.write(f"Music Mashup completed! Output file: {output_filename}")
        return True
    except Exception as e:
        st.write(f"Error: {e}")
        return False


def send_email(receiver_email, attachment_path):
    sender_email = "noreply.bhavyabhalla@gmail.com"  # Update with your email
    sender_password = "xcux sgih brob cqdg"  # Update with your email password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Your Music Mashup"

    with open(attachment_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {attachment_path}",
    )

    msg.attach(part)
    text = msg.as_string()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, text)


def main():
    st.title("Music Mashup Generator - Suhawni - 102103344")

    artist_name = st.text_input("Enter the name of artist :")
    num_videos = st.number_input("Enter number of videos to search for :", min_value=1, step=1)
    audio_duration = st.number_input("Enter time duration (in seconds) to be trimmed from starting :", min_value=1, step=1)
    receiver_email = st.text_input("Enter your email address :")

    if st.button("Generate Mashup"):
        output_filename = "102103344_output.mp3"
        if create_music_mashup('AIzaSyAzrMmAAgGJygxEkBI96aGVLTekpB_LkcY', artist_name, num_videos, audio_duration, output_filename):
            send_email(receiver_email, output_filename)
            st.success("Mashup created and sent to your email!")
            st.success("Please do check in your spam folder. It will be from mail id : noreply.bhavyabhalla@gmail.com")
        else:
            st.error("Error occurred while generating mashup.")


if __name__ == "__main__":
    main()
