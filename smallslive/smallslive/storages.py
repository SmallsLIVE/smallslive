from django.contrib.staticfiles.storage import StaticFilesStorage
from pipeline.storage import PipelineMixin
from whitenoise.django import GzipStaticFilesMixin


class PipelineGzipStorage(GzipStaticFilesMixin, PipelineMixin, StaticFilesStorage):
    pass
