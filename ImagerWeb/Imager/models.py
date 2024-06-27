from django.db import models
from django.contrib.auth.forms import User
from hashlib import sha256
from datetime import datetime

# Create your models here.

class Image(models.Model):
    user = models.ForeignKey(to=User, verbose_name='User', on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField('Image', upload_to='', null=True, blank=True)
    date = models.DateTimeField(verbose_name='Date', auto_now_add=True)
    is_private = models.BooleanField(verbose_name='Is Private', default=True)
    
    def __str__(self):
        if self.is_private:
            access = 'Private'
        else:
            access = 'Public'
        return f"{self.image.name} ({self.user.username}) {access}"
    
    def save(self, *args, **kwargs):
        self.image.name = sha256(f"{self.image.name}{str(datetime.now())}".encode('utf-8')).hexdigest() + '.' + self.image.name.rsplit('.', 1)[-1]

        super().save(*args, **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ForeignKey(to='Image', verbose_name=('Photo'), on_delete=models.CASCADE)
    plan = models.ForeignKey(to='Plan', verbose_name='Plan', on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.username}"
    
class Plan(models.Model):
    name = models.CharField(verbose_name=('Name'), max_length=20)
    space_limit = models.IntegerField(verbose_name='Space Limit')
    image_limit = models.IntegerField(verbose_name='Image Limit')
    
    def __str__(self):
        return f"{self.name}"