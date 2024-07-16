from django.db.models.signals import post_delete, post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, Plan, Image
import os

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, plan=Plan.objects.filter(name='Free').first())

@receiver(post_delete, sender=Image)
def delete_img_from_folder(sender, instance, **kwargs):
    if os.path.isfile(instance.image.path):
        os.remove(instance.image.path)