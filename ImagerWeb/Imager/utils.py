import os
from .models import Image

def get_images_size(images: Image) -> float: # size in MB
    images_size = 0
    location = f'{os.path.abspath(os.path.dirname(__name__))}/Imager/media/'
    for image in images:
        images_size += os.path.getsize(f"{location}{image['image']}")
    images_size = round(images_size / (1024*1024.0), 2)
    return images_size