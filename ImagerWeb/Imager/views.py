from django.shortcuts import render
from .models import Image
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.forms import User
from .models import Image, Profile, Plan, API, ViewedImage
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from .forms import ImageForm
from django.db.models import Q
from .utils import get_images_size, get_sort
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework import status
from django.utils.datastructures import MultiValueDictKeyError
from hashlib import sha256
from datetime import datetime
import os
from pathlib import Path

def home(request):
    context ={
    }
    return render(request, template_name='home.html', context=context)


def index(request):
    values = ('user__username', 'image', 'date', 'view_count', 'title', 'user__id')
    query = request.COOKIES.get('query', '')
    sort_option = request.COOKIES.get('sort_option', 'views_desc')
    sort = get_sort(sort_option)
    images = Image.objects.filter(is_private=False).values(*values).filter(Q(description__icontains=query) | Q(user__username__icontains=query) | Q(title__icontains=query) | Q(date__icontains=query)).order_by(sort)
    per_page = 8
    paginator = Paginator(images, per_page=per_page)
    page_number = request.GET.get('page')
    paged_images = paginator.get_page(page_number)
    for paged_image in paged_images:
        profile_photo = Profile.objects.filter(user=paged_image['user__id']).values('photo__image').first()
        paged_image['p_photo'] = profile_photo['photo__image']
    context ={
        'images': paged_images,
        'query': query,
        'views_sort_option': sort_option
    }
    return render(request, template_name='index.html', context=context)

def image(request, image_name):
    values = ('user__id', 'user__username', 'image', 'date', 'id', 'view_count', 'description', 'title')
    image = Image.objects.filter(image=image_name).values(*values).first()
    if not ViewedImage.objects.filter(user=image['user__id'], image=image['id']).exists():
        Image.objects.filter(image=image_name).update(view_count=image['view_count']+1)
        user = User.objects.filter(id=image['user__id']).first()
        viewed_img = Image.objects.filter(id=image['id']).first()
        ViewedImage.objects.create(user=user, image=viewed_img)
    profile_photo = Profile.objects.filter(user=image['user__id']).values('photo__image').first()
    image['p_photo'] = profile_photo['photo__image']
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
        if image.is_private == False and is_private == True:
            new_image_name = sha256(f"{image_name}{str(datetime.now())}".encode('utf-8')).hexdigest() + '.' + image_name.rsplit('.', 1)[-1]
            base_dir = Path(__file__).resolve().parent.parent
            old_file = os.path.join(f"{base_dir}/Imager/media", image_name)
            new_file = os.path.join(f"{base_dir}/Imager/media", new_image_name)
            Image.objects.filter(image=image_name).update(image=new_image_name, is_private=is_private, description=request.POST.get('description'), title=request.POST.get('title'))
            os.rename(old_file, new_file)
            messages.info(request, f'Image updated')
            return redirect(f'{new_image_name}')
        Image.objects.filter(image=image_name).update(is_private=is_private, description=request.POST.get('description'), title=request.POST.get('title'))
        messages.info(request, f'Image updated')
        return redirect(f'{image_name}')
    return render(request, template_name='edit_image.html', context=context)
    
    
@login_required(login_url='../accounts/login/')
def profile(request):
    if request.method == 'POST':
        if 'setProfileImageName' in request.POST:
            image_name = request.POST.get('setProfileImageName')
            try:
                image = Image.objects.get(image=image_name)
            except:
                messages.error(request, f'Image does not exist')
                return redirect(f'profile')
            profile = Profile.objects.get(user=request.user.id)
            profile.photo = image
            profile.save()
            messages.info(request, f'Profile picture set!')
            return redirect(f'profile')
        if 'deleteImageName' in request.POST:
            image_name = request.POST.get('deleteImageName')
            try:
                Image.objects.filter(image=image_name).delete()
                messages.info(request, f'Image deleted')
                return redirect(f'profile')
            except Exception as e:
                messages.error(request, e)
                return redirect(f'profile')
    values = ('user__username', 'image', 'date', 'is_private', 'id', 'title')
    per_page = 6
    query = request.COOKIES.get('query', '')
    sort_option = request.COOKIES.get('sort_option', 'views_desc')
    sort = get_sort(sort_option)
    images = Image.objects.filter(user_id=request.user.id).values(*values).filter(Q(description__icontains=query) | Q(user__username__icontains=query) | Q(title__icontains=query) | Q(date__icontains=query)).order_by(sort)
    all_images = Image.objects.filter(user_id=request.user.id).values('image')
    profile = Profile.objects.filter(user_id=request.user.id).first()
    paginator = Paginator(images, per_page=per_page)
    page_number = request.GET.get('page')
    paged_images = paginator.get_page(page_number)
    context ={
        'images': paged_images,
        'profile': profile,
        'images_count': len(all_images),
        'images_size': get_images_size(all_images),
        'query': query,
        'views_sort_option': sort_option
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
        
        User.objects.create_user(username=username, email=email, password=password)
        messages.info(request, f'User {username} registered!')
        return redirect('login')
    return render(request, 'registration/register.html')

def public_profile(request, username):
    values = ('user__username', 'image', 'date', 'title')
    per_page = 8
    query = request.COOKIES.get('query', '')
    sort_option = request.COOKIES.get('sort_option', 'views_desc')
    sort = get_sort(sort_option)
    images = Image.objects.filter(user__username=username, is_private=False).values(*values).filter(Q(description__icontains=query) | Q(user__username__icontains=query) | Q(title__icontains=query) | Q(date__icontains=query)).order_by(sort)
    paginator = Paginator(images, per_page=per_page)
    page_number = request.GET.get('page')
    paged_images = paginator.get_page(page_number)
    context ={
        'images': paged_images,
        'query': query,
        'views_sort_option': sort_option
    }
    return render(request, template_name='public_profile.html', context=context)


class UploadImageAPIView(APIView):
    def post(self, request):
        args = ('username', 'password', 'is_private', 'description')
        flag = False
        missings_args = []
        data, file = request.POST.copy(), request.FILES.copy()
        
        for arg in args:
            try:
                data[arg] 
            except MultiValueDictKeyError as e:
                flag = True
                missings_args.append(e.args[0])
        if flag:
            return Response({'Missing args error': missings_args}, status=status.HTTP_400_BAD_REQUEST)
        if not file.get('image', False):
            return Response({'Massage': 'No image was sent'}, status=status.HTTP_400_BAD_REQUEST)
 
        user = authenticate(username=request.data['username'], password=request.data['password'])
        if user is None:
            return Response({'Massage': 'Invalid Username and Password'}, status=status.HTTP_401_UNAUTHORIZED)
        
        images = Image.objects.filter(user_id=user.id).values('image')
        profile = Profile.objects.filter(user=user.id).first()
        images_count = len(images)
        images_size = get_images_size(images)
        if images_count >= profile.plan.image_limit:
            return Response({'Massage': 'You have reached the limit of the images you can have'}, status=status.HTTP_400_BAD_REQUEST)
        if (round(file['image'].size / (1024*1024.0), 2) + images_size) >= profile.plan.space_limit:
            return Response({'Massage': 'Uploading selected image will exceed the allowed space'}, status=status.HTTP_400_BAD_REQUEST)
        
        data['user'] = user
        form = ImageForm(data, file)
        if not form.is_valid():
            return Response({'Massage': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)

        form.save()
        return Response({ "Success":"Image uploaded"}, status=status.HTTP_200_OK)
    
class ValidateUserAPIView(APIView):
    def post(self, request):
        args = ('username', 'password')
        flag = False
        missings_args = []
        data = request.data.copy()
        
        for arg in args:
            try:
                data[arg] 
            except MultiValueDictKeyError as e:
                flag = True
                missings_args.append(e.args[0])
        if flag:
            return Response({'Missing args error': missings_args}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            return Response({'Massage': 'Invalid Username and Password'}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({ "Success":"User is valid"}, status=status.HTTP_200_OK)
            