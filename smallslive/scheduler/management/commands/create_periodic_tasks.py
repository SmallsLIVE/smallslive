from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule

import json
from datetime import timedelta

class Command(BaseCommand):
    help = "Create all periodic tasks previously on Heroku"

    def handle(self, *args, **kwargs):
        tasks = [
            {"name": "Fetch Newsletters", "task": "scheduler.tasks.fetch_newsletters_task", "hour": 19, "minute": 0},
            {"name": "Import S3 Audio", "task": "scheduler.tasks.import_s3_audio_task", "hour": 9, "minute": 0},
            {"name": "Import S3 Video", "task": "scheduler.tasks.import_s3_video_task", "hour": 9, "minute": 30},
            {"name": "Import S3 Video Mezzrow", "task": "scheduler.tasks.import_s3_video_mezzrow_task", "hour": 10, "minute": 0},
            {"name": "Import S3 Audio Mezzrow", "task": "scheduler.tasks.import_s3_audio_mezzrow_task", "hour": 10, "minute": 30},
            {"name": "Import S3 Video Jazzcultural", "task": "scheduler.tasks.import_s3_video_jazzcultural_task", "hour": 11, "minute": 0},
            {"name": "Import S3 Audio Jazzcultural", "task": "scheduler.tasks.import_s3_audio_jazzcultural_task", "hour": 11, "minute": 30},
        ]

        for t in tasks:
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=str(t["minute"]),
                hour=str(t["hour"]),
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
            )

            PeriodicTask.objects.update_or_create(
                name=t["name"],
                defaults={
                    "crontab": schedule,
                    "task": t["task"],
                    "args": json.dumps([]),
                    "kwargs": json.dumps({}),
                    "enabled": True,
                },
            )

            # Create interval-based test task (every 30 seconds)
            interval, _ = IntervalSchedule.objects.get_or_create(
                every=30,
                period=IntervalSchedule.SECONDS,
            )

            PeriodicTask.objects.update_or_create(
                name="Test Task Every 30s",
                defaults={
                    "interval": interval,
                    "task": "scheduler.tasks.test_celery_task",
                    "args": json.dumps([]),
                    "kwargs": json.dumps({}),
                    "enabled": True,
                },
            )

            self.stdout.write(self.style.SUCCESS(f"Periodic task '{t['name']}' created/updated."))
