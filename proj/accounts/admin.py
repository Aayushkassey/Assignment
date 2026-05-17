from django.contrib import admin 
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User 
from assignments.models import LabWork, Submission
# Register your models here.

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'name', 'roll_number', 'email', 'role', 'semester', 'batch')
    search_fields = ('username', 'name', 'roll_number', 'email')
    list_filter = ('role', 'semester', 'batch')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('name', 'roll_number', 'role', 'semester', 'batch')}),
    )

admin.site.register(User, UserAdmin)


class LabWorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'semester', 'batch', 'created_at', 'deadline')
    search_fields = ('title', 'teacher__username', 'semester', 'batch')
    list_filter = ('semester', 'batch')

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'lab', 'submitted_at', 'semester', 'batch')
    search_fields = ('student__username', 'lab__title')
    list_filter = ('submitted_at','semester', 'batch')
admin.site.register(LabWork, LabWorkAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.site_header = "Assignment Admin"
admin.site.site_title = "Assignment Admin Portal"