from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Image
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
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