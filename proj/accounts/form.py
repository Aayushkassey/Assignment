from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class StudentTeacherRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=[
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ], widget=forms.Select(attrs={'class': 'form-control'}))

    roll_number = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    batch = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    semester = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
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
        
        readonly_fields = ['name', 'email', 'roll_number']
        
        for field_name, field in self.fields.items():
            
            field.widget.attrs.update({'class': 'form-control'})
            
        
            if field_name in readonly_fields:
                field.widget.attrs['readonly'] = True
                field.widget.attrs.update({'style': 'background-color: #e9ecef; cursor: not-allowed;'})