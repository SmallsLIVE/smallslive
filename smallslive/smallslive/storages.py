from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from pipeline.storage import PipelineMixin
from whitenoise.django import GzipStaticFilesMixin


class PipelineGzipStorage(GzipStaticFilesMixin, PipelineMixin, ManifestStaticFilesStorage):
    # don't normalize paths in the CSS file, make pipeline and manifest storage work together
    patterns = []
