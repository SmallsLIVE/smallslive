import floppyforms
from django import forms
from django_thumbor import generate_url
from image_cropping.widgets import CropWidget, get_attrs

class ImageThumbnailWidget(floppyforms.ClearableFileInput):
    template_name = 'form_widgets/image_widget.html'


class ImageSelectWidget(floppyforms.Select):
    template_name = 'form_widgets/select_images.html'


class ImageCropWidget(ImageThumbnailWidget, CropWidget):

    def _media(self):
        js = [
            "",
        ]

        css = {
            "all": [
                "image_cropping/css/jquery.Jcrop.min.css",
                "image_cropping/css/image_cropping.css",
            ]
        }

        return forms.Media(css=css, js=js)

    media = property(_media)

    def render(self, name, value, attrs=None, renderer=None):
        if not attrs:
            attrs = {}
        if value:
            new_attrs = get_attrs(value, name)
            # fix to make it work with thumbor instead of easy_thumbnails
            if hasattr(value, 'url'):
                # Hack to get rid of the signature which we don't need
                # TODO: find a better way
                url = value.url.split('?')[0]
                new_attrs['data-thumbnail-url'] = generate_url(url, width=400)
            attrs.update(new_attrs)
        return super(ImageThumbnailWidget, self).render(name, value, attrs)
