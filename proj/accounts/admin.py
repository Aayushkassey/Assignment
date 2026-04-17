from django.contrib import admin
from .models import User
from assignments.models import LabWork, Submission
# Register your models here.
admin.site.register(User)
admin.site.register(LabWork)
admin.site.register(Submission)
admin.site.site_header = "Assignment Admin"
admin.site.site_title = "Assignment Admin Portal"