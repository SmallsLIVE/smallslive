import floppyforms
import logging

from django.conf import settings
from django import forms
from utils.cloudinary_utils import generate_url
from image_cropping.widgets import CropWidget, get_attrs

logger = logging.getLogger(__name__)


class ImageThumbnailWidget(floppyforms.ClearableFileInput):
    template_name = 'form_widgets/image_widget.html'


class ImageSelectWidget(floppyforms.Select):
    template_name = 'form_widgets/select_images.html'


class ImageCropWidget(ImageThumbnailWidget, CropWidget):

    def _media(self):

        css = {
            "all": [
                "image_cropping/css/jquery.Jcrop.min.css",
                "image_cropping/css/image_cropping.css",
            ]
        }

        return forms.Media(css=css)

    media = property(_media)

    def render(self, name, value, attrs=None, renderer=None):
        if not attrs:
            attrs = {}
        if value:
            new_attrs = get_attrs(value, name)
            # fix to make it work with thumbor instead of easy_thumbnails
            if hasattr(value, 'url'):
                try:
                    new_attrs['data-thumbnail-url'] = generate_url(value.file.name, value.storage.bucket.name, width=400)
                except OSError as E:
                    logger.error(str(E), exc_info=True)
            attrs.update(new_attrs)
        return super(ImageThumbnailWidget, self).render(name, value, attrs)
