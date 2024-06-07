from django.db import models
from django.conf import settings

# Create your models here.

class ImageData(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Username', on_delete=models.CASCADE, null=True)
    image = models.ImageField('Image', upload_to='', null=True, blank=True)