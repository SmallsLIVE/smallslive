from rest_framework import fields, serializers
from .models import UserVideoMetric


class UserVideoMetricSerializer(serializers.ModelSerializer):

    event_date = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S')

    class Meta:
        model = UserVideoMetric
        validators = []
        fields = '__all__'


class MonthMetricsSerializer(serializers.Serializer):
    dates = fields.ListField(
        child=fields.CharField(min_length=3, max_length=5)
    )
    video_minutes_list = fields.ListField(
        child=fields.IntegerField(min_value=0)
    )
    audio_minutes_list = fields.ListField(
        child=fields.IntegerField(min_value=0)
    )
    total_minutes_list = fields.ListField(
        child=fields.IntegerField(min_value=0)
    )
    video_plays_list = fields.ListField(
        child=fields.IntegerField(min_value=0)
    )
    audio_plays_list = fields.ListField(
        child=fields.IntegerField(min_value=0)
    )
    total_plays_list = fields.ListField(
        child=fields.IntegerField(min_value=0)
    )
    archive_video_minutes_list = fields.ListField(
        child=fields.IntegerField(min_value=0),
        required=False
    )
    archive_audio_minutes_list = fields.ListField(
        child=fields.IntegerField(min_value=0),
        required=False
    )
    archive_total_minutes_list = fields.ListField(
        child=fields.IntegerField(min_value=0),
        required=False
    )
    archive_video_plays_list = fields.ListField(
        child=fields.IntegerField(min_value=0),
        required=False
    )
    archive_audio_plays_list = fields.ListField(
        child=fields.IntegerField(min_value=0),
        required=False
    )
    archive_total_plays_list = fields.ListField(
        child=fields.IntegerField(min_value=0),
        required=False
    )
