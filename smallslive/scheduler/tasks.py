from celery import shared_task
from django.core.management import call_command
import os

def run_command(command_name, *args, **kwargs):
    os.environ["CRON_ENV"] = "heroku"
    call_command(command_name, *args, **kwargs)

# Define individual tasks
@shared_task
def fetch_newsletters_task():
    run_command("fetch_newsletters")

@shared_task
def import_s3_audio_task():
    run_command("import_s3_audio")

@shared_task
def import_s3_video_task():
    run_command("import_s3_video")

@shared_task
def import_s3_video_mezzrow_task():
    run_command("import_s3_video", bucket_name="MezzrowVid", venue_name="Mezzrow")

@shared_task
def import_s3_audio_mezzrow_task():
    run_command("import_s3_audio", bucket_name="Mezzrowmp3", venue_name="Mezzrow")

@shared_task
def test_celery_task():
    print("Hello World from Celery!")
    return "Hello World"
