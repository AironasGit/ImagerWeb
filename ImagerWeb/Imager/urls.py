from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('get_profile_images', views.get_profile_images, name='get_profile_images'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('upload_img/', views.upload_img, name='upload_img'),
    path('image/<str:image_name>', views.image, name='image'),
    path('public_profile/<str:username>', views.public_profile, name='public_profile'),
]
