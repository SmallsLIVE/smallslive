from pipeline.storage import PipelineMixin, PipelineStorage, PipelineCachedStorage
from whitenoise.storage import CompressedManifestStaticFilesStorage


class GzipManifestPipelineStorage(PipelineMixin, CompressedManifestStaticFilesStorage):
    pass
