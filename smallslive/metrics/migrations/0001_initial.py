# Generated by Django 2.2 on 2023-08-29 10:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserVideoMetric',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recording_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('last_ping', models.DateTimeField(auto_now=True)),
                ('seconds_played', models.IntegerField(default=0)),
                ('play_count', models.IntegerField(default=1)),
                ('event_id', models.PositiveIntegerField()),
                ('event_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('recording_type', models.CharField(choices=[('A', 'Audio'), ('V', 'Video')], max_length=1)),
            ],
            options={
                'unique_together': {('recording_id', 'user_id', 'date')},
            },
        ),
    ]