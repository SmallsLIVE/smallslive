import logging
import urllib
from datetime import timedelta
from django.conf import settings
from django.core import signing
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import generics, status, views
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserVideoMetric
from .serializers import MonthMetricsSerializer, UserVideoMetricSerializer

logger = logging.getLogger(__name__)


class MetricView(generics.CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = UserVideoMetric
    serializer_class = UserVideoMetricSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        signed_data = request.data.get('signed_data')
        data = signing.loads(signed_data)
        # if not self.headers_validation(request):
        #     return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            try:
                now = timezone.now()
                metric = UserVideoMetric.objects.select_for_update().get(
                    recording_id=serializer.validated_data.get('recording_id'),
                    recording_type=serializer.validated_data.get('recording_type'),
                    event_id=serializer.validated_data.get('event_id'),
                    user_id=serializer.validated_data.get('user_id'),
                    date=now.date()
                )
                if self.passes_validation(now, metric, request.user):
                    http_status = status.HTTP_204_NO_CONTENT
                    metric.seconds_played = F('seconds_played') + settings.PING_INTERVAL
                    if (metric.last_ping + timedelta(hours=1) < now):
                        metric.play_count = F('play_count') + 1
                    metric.last_ping = now
                    metric.save()
                else:
                    http_status = status.HTTP_403_FORBIDDEN
            except UserVideoMetric.DoesNotExist:
                self.perform_create(serializer)
                http_status = status.HTTP_201_CREATED
        return Response(status=http_status)

    def passes_validation(self, now, metric, user):
        allowed_ping_interval = (now >= (metric.last_ping + timedelta(seconds=settings.PING_INTERVAL_WITH_BUFFER)))
        less_than_daily_limit = metric.seconds_played < settings.DAILY_LIMIT_PER_MEDIA
        passes_validation = allowed_ping_interval and less_than_daily_limit
        if not passes_validation:
            logger.warning("User {} failed validation, U_ID:{}, R_ID:{}, SEC:{}".format(
                user.email, user.id, metric.recording_id, metric.seconds_played))
        return passes_validation

    # def headers_validation(self, request):
    #     host_header = request.META.get('HTTP_REFERER')
    #     host_header_valid = host_header and host_header.startswith(settings.SMALLSLIVE_SITE)
    #     return host_header_valid

    def perform_create(self, serializer):
        serializer.save()

metric_view = MetricView.as_view()


class EventCountsView(views.APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            month = int(request.query_params.get('month'))
            year = int(request.query_params.get('year'))
        except TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        event_id = request.query_params.get('event_id')
        if event_id:
            counts = UserVideoMetric.objects.date_counts(month, year, [int(event_id)])
        else:
            counts = UserVideoMetric.objects.date_counts(month, year)
        s = MonthMetricsSerializer(data=counts)
        if s.is_valid():
            return Response(data=s.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

event_counts = EventCountsView.as_view()


class ArtistCountsView(views.APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        try:
            month = int(request.data.get('month'))
            year = int(request.data.get('year'))
            event_ids = request.data.get('event_ids')
        except TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        counts = UserVideoMetric.objects.date_counts(month, year, event_ids)
        archive_counts = UserVideoMetric.objects.date_counts(month, year)
        for key, val in archive_counts.items():
            new_key = "archive_" + key
            counts[new_key] = val
        s = MonthMetricsSerializer(data=counts)
        if s.is_valid():
            return Response(data=s.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

artist_counts = ArtistCountsView.as_view()
