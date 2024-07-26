import os
import boto3
import logging
from datetime import datetime

from django.conf import settings

from moviepy.editor import VideoFileClip

logger = logging.getLogger(__name__)


class VideoToAudioConverter:

    def __init__(self, bucket_name):
        self.bucket = bucket_name
        self.conn = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='us-east-1',
        )

    def __download_video_file_from_s3(self, filename):
        write_file_name = f'tmp_video_{datetime.now().timestamp()}.mp4'

        print(write_file_name)
        with open(write_file_name, 'wb') as f:
            self.conn.download_fileobj(self.bucket, filename, f)

        logger.info(f"File downloaded from bucket {filename}")

        return write_file_name

    def convert_video_to_audio(self, file_name, folder_name, event_id, set_num):
        local_file_name = self.__download_video_file_from_s3(file_name)