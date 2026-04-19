from django.contrib import admin
from .models import User
from assignments.models import LabWork, Submission
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'roll_number', 'email', 'role', 'semester', 'batch')
    search_fields = ('username', 'name', 'roll_number', 'email')
    list_filter = ('role', 'semester', 'batch')
admin.site.register(User, UserAdmin)

admin.site.register(LabWork)
admin.site.register(Submission)
admin.site.site_header = "Assignment Admin"
admin.site.site_title = "Assignment Admin Portal"