import os
from .models import Image
from django.db.models import Q
from pathlib import Path

def get_images_size(images: Image) -> float: # size in MB
    images_size = 0
    base_dir = Path(__file__).resolve().parent.parent
    location = f'{base_dir}/Imager/media/'
    for image in images:
        images_size += os.path.getsize(f"{location}{image['image']}")
    images_size = round(images_size / (1024*1024.0), 2)
    return images_size

def get_sort(sort_option):
    match sort_option:
        case 'views_asc':
            sort = 'view_count'
        case 'views_desc':
            sort = '-view_count'
        case 'date_asc':
            sort = 'date'
        case 'date_desc':
            sort = '-date'
        case _:
            sort = '-view_count'
    return sort