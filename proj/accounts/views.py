from django.shortcuts import redirect, render
from .form import StudentTeacherRegistrationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm

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