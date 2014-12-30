from django.contrib.staticfiles.storage import ManifestStaticFilesStorage, StaticFilesStorage
from pipeline.storage import PipelineMixin, GZIPMixin


class PipelineGzipStorage(PipelineMixin, StaticFilesStorage):
    # don't normalize paths in the CSS file, make pipeline and manifest storage work together
    patterns = []
