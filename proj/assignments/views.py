from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LabWork, Submission
from django.contrib.auth import get_user_model

User = get_user_model()

def home(request):
    return render(request, 'assignments/home.html')


@login_required
def dashboard(request):
    show_profile = request.GET.get('profile')
    if request.user.role == 'student':
        # Students see labs matching their own semester and batch
        labs = LabWork.objects.filter(
            semester=request.user.semester,
            batch=request.user.batch
        )
        submitted_lab_ids = Submission.objects.filter(
            student=request.user
        ).values_list('lab_id', flat=True)
        
        return render(request, 'assignments/dashboard.html', {
            'labs': labs,
            'submitted_lab_ids': list(submitted_lab_ids),
            'show_profile': show_profile,  # Flag to show profile link in navbar
        })
    
    else:
        # TEACHER LOGIC
        selected_batch = request.GET.get('batch')
        selected_semester = request.GET.get('semester')

        # Dropdown options
        all_batches = LabWork.objects.values_list('batch', flat=True).distinct().order_by('-batch')
        all_semesters = LabWork.objects.values_list('semester', flat=True).distinct().order_by('semester')

        # Teacher's Assignments
        labs = LabWork.objects.filter(teacher=request.user)

        # Student Directory (Hierarchy ko lagi ordering milayeko)
        students = User.objects.filter(role='student').order_by('batch', 'semester', 'roll_number')

        # Filters apply garne
        if selected_batch:
            labs = labs.filter(batch=selected_batch)
            students = students.filter(batch=selected_batch)
        if selected_semester:
            labs = labs.filter(semester=selected_semester)
            students = students.filter(semester=selected_semester)

        return render(request, 'assignments/dashboard.html', {
            'labs': labs,
            'students': students,
            'all_batches': all_batches,
            'all_semesters': all_semesters,
            'selected_batch': selected_batch,
            'selected_semester': selected_semester,
            'show_profile': show_profile,  # Flag to show profile link in navbar
        })
@login_required
def upgrade_semester(request):
    if request.user.role != 'teacher':
        return redirect('dashboard')

    if request.method == 'POST':
        batch_to_upgrade = request.POST.get('batch_to_upgrade')
        current_sem = request.POST.get('current_sem')
        
        try:
            # Logic: Batch matching students ko semester 1 step upgrade garne
            students = User.objects.filter(batch=batch_to_upgrade, semester=current_sem, role='student')
            
            if students.exists():
                new_sem = str(int(current_sem) + 1)
                count = students.update(semester=new_sem)
                messages.success(request, f"Success! {count} students of Batch {batch_to_upgrade} moved to Semester {new_sem}.")
            else:
                messages.warning(request, "No students found matching this criteria.")
                
        except ValueError:
            messages.error(request, "Invalid input. Please use numbers for semester.")

    return redirect('dashboard')

@login_required
def lab_detail(request, pk):
    if request.user.role == 'student':
        # Security: Ensure student can only access labs matching their semester AND batch
        lab = get_object_or_404(
            LabWork, 
            pk=pk, 
            semester=request.user.semester,
            batch=request.user.batch
        )
    else:
        lab = get_object_or_404(LabWork, pk=pk, teacher=request.user)

    if request.method == "POST":
        code_content = request.POST.get('code_content')
        Submission.objects.update_or_create(
            student=request.user,
            lab=lab,
            defaults={
                'code': code_content,
                'name': request.user.name,
                'batch': request.user.batch,
                'roll_number': request.user.roll_number,
                'semester': request.user.semester,
                }
        )
        return redirect('dashboard')

    submission = Submission.objects.filter(student=request.user, lab=lab).first()
    
    return render(request, 'assignments/dashboard.html', {
        'selected_lab': lab,
        'submission': submission,
    })

@login_required
def add_lab(request):
    if request.user.role != 'teacher':
        return redirect('dashboard')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        semester = request.POST.get('semester')
        batch = request.POST.get('batch')  # Get batch from form
        deadline = request.POST.get('deadline')

        LabWork.objects.create(
            teacher=request.user,
            title=title,
            description=description,
            semester=semester,
            batch=batch, # Save batch
            deadline=deadline
        )
        return redirect('dashboard')
        
    return render(request, 'assignments/add_lab.html')

def edit_lab(request, lab_id):
    if request.user.role != 'teacher':
        return redirect('dashboard')
        
    lab = get_object_or_404(LabWork, id=lab_id, teacher=request.user)
    
    if request.method == 'POST':
        lab.title = request.POST.get('title')
        lab.description = request.POST.get('description')
        lab.semester = request.POST.get('semester')
        lab.batch = request.POST.get('batch')  # Update batch
        lab.deadline = request.POST.get('deadline')
        lab.save()
        return redirect('dashboard')
    
    return render(request, 'assignments/edit_lab.html', {'lab': lab})

def delete_lab(request, lab_id):
    if request.user.role != 'teacher':
        return redirect('dashboard')
        
    lab = get_object_or_404(LabWork, id=lab_id, teacher=request.user)
    lab.delete()
    return redirect('dashboard')

@login_required
def view_submissions(request, lab_id):
    if request.user.role != 'teacher':
        return redirect('dashboard')
        
    lab = get_object_or_404(LabWork, id=lab_id, teacher=request.user)
    # select_related makes the query faster by joining user data
    submissions = Submission.objects.filter(lab=lab).select_related('student')
    
    return render(request, 'assignments/view_submissions.html', {
        'lab': lab,
        'submissions': submissions
    })

@login_required
def delete_submissions(request):
    if request.user.role == 'teacher' and request.method == 'POST':
        submission_ids = request.POST.getlist('submission_ids')
        Submission.objects.filter(id__in=submission_ids).delete()
        messages.success(request, "Deleted successfully!")
    return redirect('dashboard')

@login_required
def view_profile(request):
    
    return render(request, 'assignments/view_profile.html', {'show_profile': True})

def compiler(request):
    # This is a standalone helper if needed
    code = request.POST.get('code', '') if request.method == 'POST' else ''
    return render(request, 'assignments/compiler.html', {'code': code})