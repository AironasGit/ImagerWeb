from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import ImageData
from django.contrib.auth.decorators import login_required
# Create your views here.

def index(request):
    image_data_list = ImageData.objects.all()
    context = {
        #'image_data_list': image_data_list
    }
    return render(request, template_name='index.html', context=context)

def get_images(request):
    if request.GET['action'] == 'none':
        return JsonResponse({})
    images = ImageData.objects.all()
    return JsonResponse({"images": list(images.values())})

@login_required(login_url='../accounts/login/')
def profile(request):
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1
    context = {
        'num_visits': num_visits,
    }
    return render(request, template_name='profile.html', context=context)