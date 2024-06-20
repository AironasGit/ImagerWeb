from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Image
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.forms import User
from .models import Image, Profile, Plan
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from datetime import datetime
from django.core.paginator import Paginator
from .forms import ImageForm
from django.core.files.uploadedfile import InMemoryUploadedFile
from hashlib import sha256
from datetime import datetime
import os
# Create your views here.

def index(request):
    values = ('user__username', 'image', 'date')
    images = Image.objects.filter(is_private=False).values(*values)
    paginator = Paginator(images, per_page=9)
    page_number = request.GET.get('page')
    paged_images = paginator.get_page(page_number)
    context ={
        'images': paged_images
    }
    return render(request, template_name='index.html', context=context)

def image(request, image_name):
    values = ('user__id', 'user__username', 'image', 'date', 'id')
    image = Image.objects.filter(image=image_name).values(*values)
    context ={
        'image': image[0]
    }
    return render(request, template_name='image.html', context=context)

@login_required(login_url='../accounts/login/')
def profile(request):
    if request.method == "POST":
        set_profile_photo(request)
    values = ('user__username', 'image', 'date', 'is_private')
    images = Image.objects.filter(user_id=request.user.id).values(*values)
    profile = Profile.objects.filter(user_id=request.user.id)
    
    details = {}
    details['images_count'] = Image.objects.filter(user_id=request.user.id).count()
    details['images_size'] = get_images_size(images)
    
    paginator = Paginator(images, per_page=9)
    page_number = request.GET.get('page')
    paged_images = paginator.get_page(page_number)
    context ={
        'images': paged_images,
        'profile': profile[0],
        'details': details
    }
    return render(request, template_name='profile.html', context=context)

@login_required(login_url='../accounts/login/')
def get_profile_images(request):
    images = Image.objects.filter(user=request.user)
    return JsonResponse({"images": list(images.values())})

@csrf_protect
@login_required(login_url='../accounts/login/')
def upload_img(request):
    redirect_url = 'upload_img'
    if request.method == "POST":
        
        if not request.POST.get('isPrivate', False):
            is_private = False
        else:
            is_private = True
            
        data, file = request.POST.copy(), request.FILES.copy()
        
        
        images_count = Image.objects.filter(user_id=request.user.id).count()
        images_size = get_images_size(Image.objects.filter(user_id=request.user.id).values('image'))
        profile = Profile.objects.filter(user=request.user.id)
        
        if images_count >= profile[0].plan.image_limit:
            messages.error(request, f'You have reached the limit of the images you can have')
            return redirect(redirect_url)
        
        if not file.get('image', False):
            messages.error(request, f'No image was selected')
            return redirect(redirect_url)
        
        if (round(file['image'].size / (1024*1024.0), 2) + images_size) >= profile[0].plan.space_limit:
            messages.error(request, f'Uploading selected image will exceed the allowed space')
            return redirect(redirect_url)
        
        file_name, file_extension = file['image'].name.split('.', 1)
        file_name = f"{file_name}{str(datetime.now())}"
        hashed_file_name = sha256(file_name.encode('utf-8')).hexdigest()
        new_file_name = f"{hashed_file_name}.{file_extension}"
        
        file_with_changed_name = InMemoryUploadedFile(file = file['image'].file, field_name=file['image'].field_name, content_type=file['image'].content_type, size=file['image'].size, charset=file['image'].charset, content_type_extra=file['image'].content_type_extra,
            name=new_file_name)
        file['image'] = file_with_changed_name
        data['user'] = request.user
        data['is_private'] = is_private
        form = ImageForm(data, file)
        
        if form.is_valid():
            form.save()
            messages.info(request, f'Image uploaded!')
            return redirect(redirect_url)
        return redirect(redirect_url)
        
    return render(request, 'upload_img.html')

@csrf_protect
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if username == '' or email == '' or password == '' or password2 == '':
            messages.error(request, f'One or more fields are empty!')
            return redirect('register')
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Username {username} already exists!')
                return redirect('register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, f'This {email} email is taken!')
                    return redirect('register')
                else:
                    try:
                        validate_password(password)
                    except ValidationError as e:
                        for error in e:
                            messages.error(request, error)
                        return redirect('register')
                    User.objects.create_user(username=username, email=email, password=password)
                    messages.info(request, f'User {username} registered!')
                    return redirect('login')
        else:
            messages.error(request, 'Passwords are not matching')
            return redirect('register')
    return render(request, 'registration/register.html')

def public_profile(request, username):
    values = ('user__username', 'image', 'date')
    images = Image.objects.filter(user__username=username, is_private=False).values(*values)
    paginator = Paginator(images, per_page=9)
    page_number = request.GET.get('page')
    paged_images = paginator.get_page(page_number)
    context ={
        'images': paged_images
    }
    return render(request, template_name='public_profile.html', context=context)


def set_profile_photo(request):
    profile = Profile.objects.get(user=request.user.id)
    image_id = request.POST['imageId']
    image = Image.objects.get(id=image_id)
    profile.photo = image
    profile.save()

def get_images_size(images): # size in MB
    images_size = 0
    for image in images:
        images_size = images_size + os.path.getsize(f"{os.path.abspath(os.path.dirname(__name__))}/Imager/media/{image['image']}")
    images_size = round(images_size / (1024*1024.0), 2)
    return images_size

