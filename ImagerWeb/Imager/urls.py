from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('upload_img/', views.upload_img, name='upload_img'),
    path('image/<str:image_name>', views.image, name='image'),
    path('public_profile/<str:username>', views.public_profile, name='public_profile'),
    path('profile/', views.set_profile_photo, name='set_profile_photo'),
    path('edit_image/<str:image_name>', views.edit_image, name='edit_image'),
]
