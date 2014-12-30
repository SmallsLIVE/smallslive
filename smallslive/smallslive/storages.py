from django.contrib.staticfiles.storage import ManifestStaticFilesStorage, StaticFilesStorage
from pipeline.storage import PipelineMixin
from whitenoise.django import GzipStaticFilesMixin


class PipelineGzipStorage(GzipStaticFilesMixin, PipelineMixin, StaticFilesStorage):
    # don't normalize paths in the CSS file, make pipeline and manifest storage work together
    patterns = []
