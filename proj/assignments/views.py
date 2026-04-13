from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import LabWork, Submission


def home(request):
    return render(request, 'assignments/home.html')

@login_required
def dashboard(request):
    if request.user.role == 'student':
        labs = LabWork.objects.filter(semester=request.user.semester)
        submitted_lab_ids = Submission.objects.filter(
            student=request.user
        ).values_list('lab_id', flat=True)
    else:
        labs = LabWork.objects.filter(teacher=request.user)
        submitted_lab_ids = []

    return render(request, 'assignments/dashboard.html', {
        'labs': labs,
        'submitted_lab_ids': submitted_lab_ids
    })

@login_required
def lab_detail(request, pk):
    if request.user.role == 'student':
        lab = get_object_or_404(LabWork, pk=pk, semester=request.user.semester)
    else:
        lab = get_object_or_404(LabWork, pk=pk)

    if request.method == "POST":
        code_content = request.POST.get('code_content')
        Submission.objects.update_or_create(
            student=request.user,
            lab=lab,
            defaults={'code': code_content}
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
        deadline = request.POST.get('deadline')

        LabWork.objects.create(
            teacher=request.user,
            title=title,
            description=description,
            semester=semester,
            deadline=deadline
        )
        return redirect('dashboard')
    return render(request, 'assignments/add_lab.html')

def compiler(request):
    if request.method == 'POST':
        code = request.POST.get('code')

    return render(request, 'assignments/compiler.html', {'code': code})

@login_required
def view_submissions(request, lab_id):
    if request.user.role != 'teacher':
        return redirect('dashboard')
        
    lab = get_object_or_404(LabWork, id=lab_id, teacher=request.user)
    submissions = Submission.objects.filter(lab=lab).select_related('student')
    
    return render(request, 'assignments/view_submissions.html', {
        'lab': lab,
        'submissions': submissions
    })

@login_required
def profile_view(request):
    return render(request, 'assignments/dashboard.html', {'show_profile': True})