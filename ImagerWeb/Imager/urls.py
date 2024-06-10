from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('get_images', views.get_images, name='get_images'),
    path('get_profile_images', views.get_profile_images, name='get_profile_images'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('upload_img/', views.upload_img, name='upload_img'),
]
