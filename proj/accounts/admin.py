from django.contrib import admin
from .models import User
from assignments.models import LabWork
# Register your models here.
admin.site.register(User)
admin.site.register(LabWork)
admin.site.site_header = "Assignment Management Admin"
admin.site.site_title = "Assignment Management Admin Portal"