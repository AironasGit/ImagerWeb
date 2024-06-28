from django.contrib import admin
from .models import Image, Profile, Plan

from django.db import transaction
# Register your models here.

class ImageAdmin(admin.ModelAdmin):
    def delete_queryset(self, request, queryset):
        with transaction.atomic():
           for obj in queryset:
               obj.delete()

admin.site.register(Image, ImageAdmin)
admin.site.register(Profile)
admin.site.register(Plan)
 