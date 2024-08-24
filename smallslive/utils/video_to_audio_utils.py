import os
import boto3
import logging
from datetime import datetime

from django.conf import settings
from botocore.exceptions import ClientError

from moviepy.editor import VideoFileClip

logger = logging.getLogger(__name__)


class VideoToAudioConverter:

    def __init__(self, bucket_name):
        self.video_file_bucket = bucket_name
        self.conn = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='us-east-1',
        )

        self.audio_file_bucket = {
            'smallslivevid': 'smallslivemp3',
            'MezzrowVid': 'Mezzrowmp3',
            'localvideotest': 'localvideotest',
        }

    def __convert_to_audio(self, video_file_name, audio_file_name):
        video_clip = VideoFileClip(video_file_name)

        audio_clip = video_clip.audio
        audio_clip.write_audiofile(audio_file_name)

        audio_clip.close()
        video_clip.close()

        logger.info("Audio converted successfully!!")

    def __upload_to_bucket(self, folder_name, audio_file_name):
        audio_file_bucket = self.audio_file_bucket[self.video_file_bucket]
        if audio_file_bucket == 'localvideotest':
            folder_name = f'mp3/{folder_name}'

        print("Uploading audio to bucket")
        logger.info("Uploading audio to bucket")
        try:
            self.conn.upload_file(audio_file_name, audio_file_bucket, f'{folder_name}/{audio_file_name}')
            logger.info("Uploading audio to bucket complete")
            print("Uploading audio to bucket complete")
        except ClientError as e:
            logging.error(e)
            return False

    def __download_video_file_from_s3(self, filename):
        write_file_name = f'tmp_video_{datetime.now().timestamp()}.mp4'
        logger.info(f"Fetching file from bucket {filename}")
        print("Fetching file from bucket")
        with open(write_file_name, 'wb') as f:
            self.conn.download_fileobj(self.video_file_bucket, filename, f)

        logger.info(f"File downloaded from bucket {filename}")
        print("File download complete")

        return write_file_name

    def convert_video_to_audio(self, file_name, folder_name, event_id, set_num):
        try:
            audio_file_name = f'{event_id}-{set_num}.mp3'
            video_file_name = self.__download_video_file_from_s3(file_name)

            self.__convert_to_audio(video_file_name, audio_file_name)
            self.__upload_to_bucket(folder_name, audio_file_name)

            os.remove(video_file_name)
            os.remove(audio_file_name)
            print("Video to Audio converted successfully!!!")
            logger.info("Video to Audio converted successfully!!!")
        except Exception as E:
            logger.error("Video to audio convert failed!!!")
            print("Video to audio convert failed!!!")
            logger.error(str(E), exc_info=True)
            print(str(E))
