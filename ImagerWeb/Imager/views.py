from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Image
from django.contrib.auth.decorators import login_required
from django.core import serializers
# Create your views here.

def index(request):
    image_data_list = Image.objects.all()
    context = {
        #'image_data_list': image_data_list
    }
    return render(request, template_name='index.html', context=context)

def get_images(request):
    values = ('user__username', 'image', 'date')
    images = Image.objects.filter(is_private=False).values(*values)
    return JsonResponse({'data': list(images.values(*values))})

@login_required(login_url='../accounts/login/')
def profile(request):
    context = {
    }
    return render(request, template_name='profile.html', context=context)

@login_required(login_url='../accounts/login/')
def get_profile_images(request):
    images = Image.objects.filter(user=request.user)
    return JsonResponse({"images": list(images.values())})