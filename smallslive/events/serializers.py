from rest_framework import serializers, fields
from .models import Event, Venue


# TODO Copied from django app
class MonthMetricsSerializer(serializers.Serializer):
  
    dates = fields.ListField(
        child=fields.DateField()
    )
    total_minutes_list = fields.ListField(
        child=fields.IntegerField(min_value=0)
    )
    total_plays_list = fields.ListField(
        child=fields.IntegerField(min_value=0)
    )
    


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ['id','name','audio_bucket_name','video_bucket_name','foundation']

class EventSerializer(serializers.ModelSerializer):
    venue = VenueSerializer(read_only=True)

    class Meta:
        model = Event
        fields = '__all__'