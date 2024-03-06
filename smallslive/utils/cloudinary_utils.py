import logging

from cloudinary.utils import cloudinary_url
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)


def get_transformation_list(height, width, crop_box, smart):
    transformations = []
    default_transformation = {
        'height': height,
        'width': width,
        'quality': 'auto',
    }

    if smart:
        default_transformation['crop'] = 'fill'
        default_transformation['gravity'] = 'auto'

    if crop_box:
        crop_x = crop_box[0][0]
        crop_y = crop_box[0][1]
        crop_width = crop_box[1][0] - crop_x
        crop_height = crop_box[1][1] - crop_y

        transformations.append({
            'x': crop_x,
            'y': crop_y,
            'width': crop_width,
            'height': crop_height,
            'crop': 'crop',
        })
    transformations.append(default_transformation)

    return transformations


def generate_url(
        photo_name: str, bucket_name: str, height: int = None,
        width: int = None, crop_box=None, smart=False
) -> str:
    transformation = get_transformation_list(height, width, crop_box, smart)
    try:
        photo_name_with_bucket = f'{bucket_name}/{photo_name}'
        return mark_safe(cloudinary_url(photo_name_with_bucket, transformation=transformation)[0])
    except Exception as E:
        logger.error(str(E), exc_info=True)

    return ""
