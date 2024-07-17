from django.db import models
from django.contrib.auth.forms import User
from hashlib import sha256
from datetime import datetime
import os
# Create your models here.

class Image(models.Model):
    user = models.ForeignKey(to=User, verbose_name='User', on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField('Image', upload_to='')
    date = models.DateTimeField(verbose_name='Date', auto_now_add=True)
    is_private = models.BooleanField(verbose_name='Is Private', default=True)
    description = models.TextField(verbose_name='Description', null=True, blank=True, max_length=100)
    view_count = models.IntegerField(verbose_name='View Count', default=0)
    title = models.CharField(verbose_name='Title', max_length=30, null=True, blank=True)
    
    def __str__(self):
        if self.is_private:
            access = 'Private'
        else:
            access = 'Public'
        return f"{self.image.name} | {self.user.username} | {access}"
    
    def save(self, *args, **kwargs):
        try: # This block deletes previous image when the image field is updated with a new image
            this = Image.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()
            else:
                super().save(*args, **kwargs)
                return
        except: pass
        self.image.name = sha256(f"{self.image.name}{str(datetime.now())}".encode('utf-8')).hexdigest() + '.' + self.image.name.rsplit('.', 1)[-1]
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if os.path.isfile(self.image.path):
           os.remove(self.image.path)


class Profile(models.Model):
    user = models.OneToOneField(User, verbose_name=('User'), on_delete=models.CASCADE)
    photo = models.ForeignKey(to='Image', verbose_name=('Photo'), on_delete=models.SET_NULL, null=True, blank=True)
    plan = models.ForeignKey(to='Plan', verbose_name='Plan', on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return f"{self.user.username}"
    
class Plan(models.Model):
    name = models.CharField(verbose_name=('Name'), max_length=20)
    space_limit = models.IntegerField(verbose_name='Space Limit')
    image_limit = models.IntegerField(verbose_name='Image Limit')
    
    def __str__(self):
        return f"{self.name}"

class API(models.Model):
    key = models.CharField(verbose_name='Key', max_length=128)

class ViewedImage(models.Model):
    user = models.ForeignKey(to=User, verbose_name='User', on_delete=models.CASCADE)
    image = models.ForeignKey(to='Image', verbose_name='Image', on_delete=models.CASCADE)