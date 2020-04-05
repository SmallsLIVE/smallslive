from image_cropping.utils import max_cropping


def crop_artist_pictures(queryset):
    for artist in queryset:
        image = artist.photo
        if image:
            box = max_cropping(580, 580, image.width, image.height, False)
            artist.cropping = ','.join(map(lambda i: str(i), box))
            artist.save()
