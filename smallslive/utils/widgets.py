from image_cropping.widgets import CropWidget, get_attrs
from events.forms import ImageThumbnailWidget


class ImageCropWidget(ImageThumbnailWidget, CropWidget):
    def render(self, name, value, attrs=None):
        if not attrs:
            attrs = {}
        if value:
            attrs.update(get_attrs(value, name))
        return super(ImageThumbnailWidget, self).render(name, value, attrs)