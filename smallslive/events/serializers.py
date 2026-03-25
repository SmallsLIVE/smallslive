from rest_framework import serializers, fields
from .models import Event, Venue, JazzCulturalPhotos


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
    set_hours_display = serializers.SerializerMethodField()
    absolute_url = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def get_set_hours_display(self, obj):
        return obj.get_set_hours_display()

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()


class JazzPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = JazzCulturalPhotos
        fields = '__all__'