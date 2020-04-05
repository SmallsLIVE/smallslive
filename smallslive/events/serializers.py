from rest_framework import serializers, fields


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
    
