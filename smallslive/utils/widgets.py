import floppyforms
from image_cropping.widgets import CropWidget, get_attrs


class ImageThumbnailWidget(floppyforms.ClearableFileInput):
    template_name = 'form_widgets/image_widget.html'


class ImageSelectWidget(floppyforms.Select):
    template_name = 'form_widgets/select_images.html'


class ImageCropWidget(ImageThumbnailWidget, CropWidget):
    def render(self, name, value, attrs=None):
        if not attrs:
            attrs = {}
        if value:
            attrs.update(get_attrs(value, name))
        return super(ImageThumbnailWidget, self).render(name, value, attrs)
