import datetime # Standard Python datetime
from django.utils import timezone # Django ko timezone utility
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LabWork, Submission
from django.contrib.auth import get_user_model
from .models import SubmissionFile # Import if needed

User = get_user_model()

def home(request):
    return render(request, 'assignments/home.html')


@login_required
def dashboard(request):
    show_profile = request.GET.get('profile')
    if request.user.role == 'student':
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
            'show_profile': show_profile,
        })
    
    else:
        # TEACHER LOGIC
        selected_batch = request.GET.get('batch')
        selected_semester = request.GET.get('semester')

        all_batches = LabWork.objects.values_list('batch', flat=True).distinct().order_by('-batch')
        all_semesters = LabWork.objects.values_list('semester', flat=True).distinct().order_by('semester')

        # ORDER BY thapeko chhu regrouping ko lagi
        labs = LabWork.objects.filter(teacher=request.user).order_by('-batch', 'semester')
        students = User.objects.filter(role='student').order_by('batch', 'semester', 'roll_number')

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
            'show_profile': show_profile,
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
        lab = get_object_or_404(
            LabWork, 
            pk=pk, 
            semester=request.user.semester,
            batch=request.user.batch
        )
    else:
        lab = get_object_or_404(LabWork, pk=pk, teacher=request.user)

    if request.method == "POST":
        # 1. Main Submission update or create garne
        remark = request.POST.get('description')
        submission, created = Submission.objects.update_or_create(
            student=request.user,
            lab=lab,
            defaults={
                'name': request.user.name,
                'batch': request.user.batch,
                'roll_number': request.user.roll_number,
                'semester': request.user.semester,
                'description': remark,
            }
        )
        
        # 2. Purano files delete garne (Update garda duplicate nahos vanna ko lagi)
        submission.files.all().delete()

        # 3. Dynamic logic: Jati ota boxes chhan, loop lagayera save garne
        for key, value in request.POST.items():
            if key.startswith('code_content_'):
                index = key.split('_')[-1]
                filename = request.POST.get(f'filename_{index}') or f"Solution_{index}.py"
                
                # SubmissionFile model ma save garne (Hamile agi models.py ma thapeko)
                SubmissionFile.objects.create(
                    submission=submission,
                    file_name=filename,
                    code_content=value
                )
        
        messages.success(request, "Lab work submitted successfully!")
        return redirect('dashboard')

    submission = Submission.objects.filter(student=request.user, lab=lab).first()
    
    return render(request, 'assignments/dashboard.html', {
        'selected_lab': lab,
        'submission': submission,
    })

@login_required
def add_lab(request):
    if request.user.role != 'teacher':
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        # Form bata data line
        title = request.POST.get('title')
        description = request.POST.get('description')
        semester = request.POST.get('semester')
        batch = request.POST.get('batch')
        deadline_str = request.POST.get('deadline')
        
        # Resource File (PDF) line
        pdf_file = request.FILES.get('resource_file')
        
        # Date conversion garne (String lai Python Date object banaune)
        deadline_date = None
        if deadline_str:
            try:
                deadline_date = timezone.datetime.strptime(deadline_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format.")
                return render(request, 'assignments/add_lab.html')

        # Validation: Deadline purano date huna vayena
        if deadline_date and deadline_date < timezone.now().date():
            messages.error(request, "Deadline must be today or a future date.")
            # Error aauda purano data form mai rakne (Context pathayera)
            context = {
                'title': title,
                'description': description,
                'semester': semester,
                'batch': batch,
                'deadline': deadline_str
            }
            return render(request, 'assignments/add_lab.html', context)

        # Database ma save garne
        try:
            LabWork.objects.create(
                teacher=request.user,
                title=title,
                description=description,
                semester=semester,
                batch=batch,
                deadline=deadline_str, # String pathaye ni Django le handle garchha
                pdf_file=pdf_file      # Hamile models.py ma thapeko field
            )
            messages.success(request, "New Lab Assignment published successfully!")
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f"Error creating lab: {e}")
            return render(request, 'assignments/add_lab.html')

    return render(request, 'assignments/add_lab.html')

@login_required
def edit_lab(request, lab_id):
    if request.user.role != 'teacher':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    # Lab object tanne, user teacher nai ho ki nai check garne
    lab = get_object_or_404(LabWork, id=lab_id, teacher=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        semester = request.POST.get('semester')
        batch = request.POST.get('batch')
        deadline_str = request.POST.get('deadline')
        
        # Naya PDF file aayeko chha ki check garne
        new_pdf = request.FILES.get('resource_file')
        
        # Date validation
        if deadline_str:
            try:
                deadline_date = timezone.datetime.strptime(deadline_str, "%Y-%m-%d").date()
                if deadline_date < timezone.now().date():
                    messages.error(request, "Deadline must be today or a future date.")
                    return render(request, 'assignments/edit_lab.html', {'lab': lab})
                
                # Sabai thik chha vane update garne
                lab.title = title
                lab.description = description
                lab.semester = semester
                lab.batch = batch
                lab.deadline = deadline_str
                
                # Yadi naya PDF upload vako chha vane purano lai replace garne
                if new_pdf:
                    lab.pdf_file = new_pdf
                
                lab.save()
                messages.success(request, "Lab Assignment updated successfully!")
                return redirect('dashboard')
                
            except ValueError:
                messages.error(request, "Invalid date format.")
        
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
    
    # .prefetch_related('files') thapne jasle garda student le pathayeka multiple solutions load hos
    # 'files' vaneko Submission model ko SubmissionFile sanga ko Related Name ho
    submissions = Submission.objects.filter(lab=lab)\
        .select_related('student')\
        .prefetch_related('files')\
        .order_by('-submitted_at')
    
    return render(request, 'assignments/view_submissions.html', {
        'lab': lab,
        'submissions': submissions
    })

@login_required
def delete_submissions(request):
    if request.user.role == 'teacher' and request.method == 'POST':
        ids= request.POST.getlist('submission_ids')
        if ids:
            Submission.objects.filter(id__in=ids).delete()
            messages.success(request, "Deleted successfully!")
        else:
            messages.warning(request, "No submissions selected for deletion.")
    return redirect('dashboard')

@login_required
def view_profile(request):
    
    return render(request, 'assignments/view_profile.html', {'show_profile': True})

# def compiler(request):
#     # This is a standalone helper if needed
#     code = request.POST.get('code', '') if request.method == 'POST' else ''
#     return render(request, 'assignments/compiler.html', {'code': code})

@login_required
def student_status_list(request):
    if request.user.role != 'teacher':
        return redirect('dashboard')

    selected_batch = request.GET.get('batch', '')
    selected_semester = request.GET.get('semester', '')

    students = User.objects.filter(role='student')

    if selected_batch:
        students = students.filter(batch=selected_batch)
    if selected_semester:
        students = students.filter(semester=selected_semester)

    student_stats = []
    for student in students:
        assigned_labs = LabWork.objects.filter(batch=student.batch, semester=student.semester).count()
        submitted = Submission.objects.filter(student=student, lab__batch=student.batch, lab__semester=student.semester).values('lab').distinct().count()
        
        student_stats.append({
            'info': student,
            'sent': submitted,
            'assigned': assigned_labs,
            'pending': max(0, assigned_labs - submitted),
        })

    # Dropdown ko lagi unique batches
    all_batches = User.objects.filter(role='student').values_list('batch', flat=True).distinct().order_by('-batch')

    return render(request, 'assignments/student_status_list.html', { 
        'student_stats': student_stats,
        'all_batches': all_batches,
        'all_semesters': range(1, 9),
        'selected_batch': selected_batch,
        'selected_semester': selected_semester,
        'show_status': True, # Yo true bhaye pachi table dekhincha
    })