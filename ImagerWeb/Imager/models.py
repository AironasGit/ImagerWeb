from django.db import models
from django.contrib.auth.forms import User

# Create your models here.

class Image(models.Model):
    user = models.ForeignKey(to=User, verbose_name='Username', on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField('Image', upload_to='', null=True, blank=True)
    date = models.DateTimeField(verbose_name='Date', auto_now_add=True)
    is_private = models.BooleanField(verbose_name='Is Private', default=True)
    
    def __str__(self):
        return f"{self.image.name} ({self.user.username}) Private: {self.is_private}"