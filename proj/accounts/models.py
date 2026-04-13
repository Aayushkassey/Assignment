from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    IS_STUDENT = 'student'
    IS_TEACHER = 'teacher'

    ROLE_CHOICES = [
        (IS_STUDENT, 'Student'),
        (IS_TEACHER, 'Teacher'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    semester = models.CharField(max_length=10, blank=True, null=True)