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
from django.db.models import Q
from .utils import get_images_size
# Create your views here.

def index(request):
    values = ('user__username', 'image', 'date', 'view_count')
    query = request.COOKIES.get('query')
    if query == None:
        query = ''
    images = Image.objects.filter(is_private=False).values(*values).filter(Q(description__icontains=query) | Q(user__username__icontains=query))
    per_page = 8
    #images = Image.objects.filter(is_private=False, date__year='2024', date__month='06', date__day='07').values(*values)
    paginator = Paginator(images, per_page=per_page)
    page_number = request.GET.get('page')
    paged_images = paginator.get_page(page_number)
    context ={
        'images': paged_images,
        'query': query
    }
    return render(request, template_name='index.html', context=context)

def image(request, image_name):
    values = ('user__id', 'user__username', 'image', 'date', 'id', 'view_count', 'description')
    image = Image.objects.filter(image=image_name).values(*values).first()
    Image.objects.filter(image=image_name).update(view_count=image['view_count']+1)
    context ={
        'image': image
    }
    return render(request, template_name='image.html', context=context)

def edit_image(request, image_name):
    image = Image.objects.filter(image=image_name).first()
    form = ImageForm(instance=image)
    context ={
        'form': form
    }
    if request.method == 'POST':
        is_private = False
        if request.POST.get('is_private', False):
            is_private = True
        Image.objects.filter(image=image_name).update(is_private=is_private, description=request.POST.get('description'))
        messages.info(request, f'Image updated')
        return redirect(f'{image_name}')
    return render(request, template_name='edit_image.html', context=context)

    
@login_required(login_url='../accounts/login/')
def profile(request):
    if request.method == 'POST':
        set_profile_photo(request)
        messages.info(request, f'Profile picture set!')
        return redirect(f'profile')
    values = ('user__username', 'image', 'date', 'is_private', 'id')
    per_page = 6
    images = Image.objects.filter(user_id=request.user.id).values(*values)
    profile = Profile.objects.filter(user_id=request.user.id).first()
    paginator = Paginator(images, per_page=per_page)
    page_number = request.GET.get('page')
    paged_images = paginator.get_page(page_number)
    context ={
        'images': paged_images,
        'profile': profile,
        'images_count': len(images),
        'images_size': get_images_size(images)
    }
    return render(request, template_name='profile.html', context=context)

@csrf_protect
@login_required(login_url='../accounts/login/')
def upload_img(request):
    redirect_url = 'upload_img'
    if request.method == 'POST':
        is_private = False
        if request.POST.get('isPrivate', False):
            is_private = True
        data, file = request.POST.copy(), request.FILES.copy()
        images = Image.objects.filter(user_id=request.user.id).values('image')
        profile = Profile.objects.filter(user=request.user.id).first()
        images_count = len(images)
        images_size = get_images_size(images)
        
        if images_count >= profile.plan.image_limit:
            messages.error(request, f'You have reached the limit of the images you can have')
            return redirect(redirect_url)
        if not file.get('image', False):
            messages.error(request, f'No image was selected')
            return redirect(redirect_url)
        if (round(file['image'].size / (1024*1024.0), 2) + images_size) >= profile.plan.space_limit:
            messages.error(request, f'Uploading selected image will exceed the allowed space')
            return redirect(redirect_url)
        
        data['user'] = request.user
        data['is_private'] = is_private
        form = ImageForm(data, file)
        
        if form.is_valid():
            form.save()
            messages.info(request, f'Image uploaded')
            return redirect(redirect_url)
        else:
            messages.error(request, f'Something went wrong')
            return redirect(redirect_url)
        
    return render(request, 'upload_img.html')

@csrf_protect
def register(request):
    if request.method == "POST":
        redirect_url = 'register'
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        flag = False
        if username == '' or email == '' or password == '' or password2 == '':
            messages.error(request, f'One or more fields are empty!')
            flag = True
        if password != password2:
            messages.error(request, 'Passwords are not matching!')
            flag = True
        if User.objects.filter(username=username).exists():
            messages.error(request, f'This username is taken!')
            flag = True
        if User.objects.filter(email=email).exists():
            messages.error(request, f'This email is taken!')
            flag = True
        try:
            validate_password(password)
        except ValidationError as e:
            for error in e:
                messages.error(request, error)
            flag = True
        
        if flag:
            return redirect(redirect_url)
        
        #User.objects.create_user(username=username, email=email, password=password)
        messages.info(request, f'User {username} registered!')
        return redirect('login')
    return render(request, 'registration/register.html')

def public_profile(request, username):
    values = ('user__username', 'image', 'date')
    per_page = 9
    images = Image.objects.filter(user__username=username, is_private=False).values(*values)
    paginator = Paginator(images, per_page=per_page)
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

