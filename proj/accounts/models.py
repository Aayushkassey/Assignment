from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    IS_ADMIN = 'admin'
    IS_STUDENT = 'student'
    IS_TEACHER = 'teacher'

    ROLE_CHOICES = [
        (IS_ADMIN, 'Admin'),
        (IS_STUDENT, 'Student'),
        (IS_TEACHER, 'Teacher'),
    ]

    # Add these missing fields
    name = models.CharField(max_length=100, blank=True)
    roll_number = models.CharField(max_length=20, blank=True)
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    semester = models.CharField(max_length=10, blank=True, null=True)
    batch = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.username