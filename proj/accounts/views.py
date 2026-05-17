import random
from django.shortcuts import redirect, render
from django.contrib import messages 
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from .models import User
from .form import StudentTeacherRegistrationForm, UserEditForm
from django.core.mail import send_mail
from django.conf import settings
User = get_user_model()

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            # Login milena bhane yo message jancha
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

def register_view(request):
    if request.method == "POST":
        form = StudentTeacherRegistrationForm(request.POST) 
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            roll_number = form.cleaned_data['roll_number']
            semester = form.cleaned_data['semester']
            batch = form.cleaned_data['batch']

            if User.objects.filter(username=username).exists():
                messages.error(request, "This username is already taken.")
            elif User.objects.filter(name=name,  semester=semester, batch=batch).exists():
                messages.error(request, "This name is already registered.")
            # अब roll_number check गर्दा semester र batch पनि consider गरिन्छ
            elif User.objects.filter(
                roll_number=roll_number,
                semester=semester,
                batch=batch
            ).exists():
                messages.error(request, "This roll number is already registered for this semester and batch.")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "This email is already registered.")
            else:
                user = form.save()
                login(request, user)
                return redirect('dashboard')
    else:
        form = StudentTeacherRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('view_profile')
    else:
        form = UserEditForm(instance=request.user)
        if request.user.role == 'teacher':
            del form.fields['roll_number']
            del form.fields['semester']
            del form.fields['batch']
    return render(request, 'assignments/edit_profile.html', {'form': form})

def forget_password_view(request):
    step = 1
    email = name = roll_number = semester = ""

    if request.method == "POST":
        # STEP 1: Verify Identity & Generate OTP
        if 'verify_account' in request.POST:
            email = request.POST.get('email').strip()
            name = request.POST.get('name').strip()
            roll_number = request.POST.get('roll_number').strip()
            semester = request.POST.get('semester').strip()

            user = User.objects.filter(
                email=email, 
                name__iexact=name, 
                roll_number=roll_number, 
                semester=semester,
            ).first()

            if user:
                # Generate 6-digit OTP
                otp = str(random.randint(100000, 999999))
                
                # Session  OTP store 
                request.session['reset_otp'] = otp
                request.session['reset_email'] = email

                # --- REAL EMAIL LOGIC STARTS HERE ---
                subject = 'LabPortal - Password Reset OTP'
                message = f'Namaste {name},\n\nYour OTP for password reset is: {otp}.\nDo not share this with anyone.'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email]
                
                try:
                    send_mail(subject, message, email_from, recipient_list)
                    messages.success(request, f"Identity verified! OTP has been sent to {email}.")
                    step = 2
                except Exception as e:
                    messages.error(request, "Failed to send email. Please check your internet or SMTP settings.")
                # --- REAL EMAIL LOGIC ENDS HERE ---
                
            else:
                messages.error(request, "Details do not match our records.")
                
            #     print("\n" + "="*45)
            #     print(f" SECURITY KEY FOR {name.upper()}: {otp} ")
            #     print("="*45 + "\n")
                
            #     step = 2
            #     messages.success(request, "Identity verified! Please check the terminal for the OTP.")
            # else:
            #     messages.error(request, "Details do not match our records.")

        # STEP 2: Verify OTP
        elif 'verify_otp' in request.POST:
            entered_otp = request.POST.get('otp').strip()
            saved_otp = request.session.get('reset_otp')
            email = request.session.get('reset_email')

            if entered_otp == saved_otp:
                step = 3
                messages.success(request, "OTP Verified! Set your new password.")
            else:
                step = 2
                messages.error(request, "Invalid OTP! Check your Email again.")

        # STEP 3: Reset Password
        elif 'reset_password' in request.POST:
            email = request.session.get('reset_email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password == confirm_password:
                user = User.objects.filter(email=email).first()
                if user:
                    user.set_password(password)
                    user.save()
                    
                    messages.success(request, "Password updated successfully! Login now.")
                    #No reuse of OTP & Email after successful reset
                    del request.session['reset_otp']
                    del request.session['reset_email']
                    
                    return redirect('login')
            else:
                step = 3
                messages.error(request, "Passwords do not match!")

    return render(request, 'registration/forget_password.html', {
        'step': step,
        'email': email,
        'name': name,
        'roll_number': roll_number,
        'semester': semester
    })

from django.http import JsonResponse

def check_availability(request):
    username = request.GET.get('username', None)
    email = request.GET.get('email', None)
    
    data = {
        'is_taken': False,
        'suggestion': '',
        'suggestions': []  # Multiple suggestions list
    }
    
    if username:
        exists = User.objects.filter(username__iexact=username).exists()
        if exists:
            data['is_taken'] = True
            # Multiple smart suggestions generate garau
            suggestions = [
                f"{username}_2082",
                f"{username}82",
                f"{username}_student",
                f"{username}123",
            ]
            # Filter out jo already taken cha
            available = [s for s in suggestions if not User.objects.filter(username__iexact=s).exists()]
            data['suggestions'] = available[:3]  # Max 3 suggestions
            data['suggestion'] = available[0] if available else f"{username}_new"
            
    if email:
        data['is_taken'] = User.objects.filter(email__iexact=email).exists()
        if data['is_taken']:
            data['suggestion'] = "This email is already linked to an account."
            
    return JsonResponse(data)