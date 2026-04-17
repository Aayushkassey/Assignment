from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class StudentTeacherRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=[
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ], widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta(UserCreationForm.Meta):
        model = User
        # Username thapnai parchha, natra user create hunna
        fields = ("username", "name", "roll_number", "email", "role", "semester", "batch")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'roll_number', 'semester', 'batch']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})