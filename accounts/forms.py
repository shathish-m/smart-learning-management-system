from django import forms
from .models import AuthAdmin
from .models import Student
from .models import Assignment

from django.contrib.auth import get_user_model
User = get_user_model()

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = AuthAdmin
        fields = ['username', 'email', 'phone_number', 'password']


class StudentRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Student
        fields = ['username', 'email', 'phone_number', 'password']


class StudentLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)



class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'file', 'course']

