from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('upload_img/', views.upload_img, name='upload_img'),
    path('image/<str:image_name>', views.image, name='image'),
    path('public_profile/<str:username>', views.public_profile, name='public_profile'),
    path('edit_image/<str:image_name>', views.edit_image, name='edit_image'),
    
    #API
    path('api/upload_img/', views.UploadImageAPIView.as_view(), name='api_upload_img'),
    path('api/validate_user/', views.ValidateUserAPIView.as_view(), name='api_validate_user'),
]
