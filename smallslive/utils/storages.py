from pipeline.storage import PipelineMixin, PipelineStorage, PipelineCachedStorage
from whitenoise.django import GzipStaticFilesMixin, GzipManifestStaticFilesStorage


class GzipManifestPipelineStorage(PipelineMixin, GzipManifestStaticFilesStorage):
    pass
