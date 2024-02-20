import logging
import re
from urllib.parse import unquote, unquote_plus

from cloudinary import CloudinaryImage
from cloudinary.utils import cloudinary_url
from django import template
from django.utils.safestring import mark_safe

register = template.Library()
logger = logging.getLogger(__name__)


def extract_parts(photo_url):
    # Extracting subdomain
    subdomain_pattern = r'https://([^\.]+)\.'
    subdomain_match = re.search(subdomain_pattern, photo_url)
    if subdomain_match:
        subdomain = subdomain_match.group(1)
    else:
        subdomain = None

    # Extracting path after domain
    path_pattern = r'https://[^/]+(/[^ ]+)'
    path_match = re.search(path_pattern, photo_url)
    if path_match:
        path = path_match.group(1)
    else:
        path = None

    return subdomain, path


def decode_url_safe(url):
    try:
        decoded_url = unquote(url)
    except:
        # If unquoting fails, it might be already decoded or has a different encoding scheme
        try:
            decoded_url = unquote_plus(url)  # Try another decoding method
        except:
            decoded_url = url  # If both decoding attempts fail, return the original URL
    return decoded_url


def get_transformation_list(height, width, crop_box):
    transformations = []
    if crop_box:
        transformations.append({
            'x': crop_box[0][0],
            'y': crop_box[0][1],
            'width': crop_box[1][0],
            'height': crop_box[1][1],
            'crop': 'fit',
            'quality': 'auto'
        })
    transformations.append({
        'height': height,
        'width': width,
        'quality': 'auto',
    })

    return transformations


@register.simple_tag(takes_context=True)
def cloudinary_image_transform(context, photo_name, height=None, width=None, crop_box=None, photo_url=None):
    transformation = get_transformation_list(height, width, crop_box)
    if photo_name:
        try:
            return mark_safe(CloudinaryImage(photo_name).image(
                transformation=transformation
            ))
        except Exception as E:
            logger.error(str(E), exc_info=True)
    if photo_url:
        photo_url = decode_url_safe(photo_url)
        bucket_name, file_path = extract_parts(photo_url)

        if bucket_name and file_path:
            photo_name = f'{bucket_name}{file_path}'
            try:
                return mark_safe(CloudinaryImage(photo_name).image(
                    transformation=transformation
                ))
            except Exception as E:
                logger.error(str(E), exc_info=True)

        default_image = f"<img src='{photo_url}' alt='' height='{height}' width='{width}'>"
        return mark_safe(default_image)
    return ""


@register.simple_tag(takes_context=True)
def cloudinary_image_url(context, photo_name, height=None, width=None, crop_box=None, photo_url=None):
    transformation = get_transformation_list(height, width, crop_box)
    if photo_name:
        try:
            return mark_safe(cloudinary_url(photo_name, transformation=transformation)[0])
        except Exception as E:
            logger.error(str(E), exc_info=True)

    if photo_url:
        photo_url = decode_url_safe(photo_url)
        bucket_name, file_path = extract_parts(photo_url)

        if bucket_name and file_path:
            photo_name = f'{bucket_name}{file_path}'
            try:
                return mark_safe(cloudinary_url(photo_name, transformation=transformation)[0])
            except Exception as E:
                logger.error(str(E), exc_info=True)

        return mark_safe(photo_url)

    return ""

