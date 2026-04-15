from pyexpat.errors import messages

from django.shortcuts import redirect, render

from accounts.models import User
from .form import StudentTeacherRegistrationForm
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password

User = get_user_model()

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard') 
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

def register_view(request):
    if request.method == "POST":
       
        form = StudentTeacherRegistrationForm(request.POST) 
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')

    else:
        form = StudentTeacherRegistrationForm()
        
    return render(request, 'registration/register.html', {'form': form})

from django.contrib import messages # Ensure this is at the top

User = get_user_model()


def forget_password_view(request):
    step = 1
    # Retrieve data from POST to keep track of state
    username = request.POST.get('username', '')
    email = request.POST.get('email', '')

    if request.method == "POST":
        # STEP 1: Verify Identity
        if 'verify_account' in request.POST:
            user = User.objects.filter(username=username, email=email).first()
            if user:
                step = 2
                messages.success(request, f"Identity verified for {username}. Enter your new password.")
            else:
                messages.error(request, "User not found with that combination of Username and Email.")

        # STEP 2: Update Password
        elif 'reset_password' in request.POST:
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password == confirm_password:
                # We filter again by username to be absolutely sure
                user = User.objects.get(username=username)
                user.password = make_password(new_password)
                user.save()
                messages.success(request, "Password updated! Please login with your new credentials.")
                return redirect('login')
            else:
                messages.error(request, "Passwords do not match.")
                step = 2

    return render(request, 'registration/forget_password.html', {
        'step': step,
        'username': username,
        'email': email
    })