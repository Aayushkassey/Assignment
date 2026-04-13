# assignments/models.py
from django.conf import settings
from django.db import models

# assignments/models.py
class LabWork(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'teacher'} 
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    semester = models.CharField(max_length=10) 
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()

    def __str__(self):
        return self.title
    
class Submission(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'student'} 
    )
    lab = models.ForeignKey(LabWork, on_delete=models.CASCADE)
    code = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.lab.title}"