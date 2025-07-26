# cwc_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['station', 'title', 'description', 'location', 'evidence']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class CriminalForm(forms.ModelForm):
    class Meta:
        model = Criminal
        fields = ['name', 'photo', 'age', 'gender', 'address', 'crimes', 'status']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'crimes': forms.Textarea(attrs={'rows': 3}),
        }

class PoliceStationForm(forms.ModelForm):
    class Meta:
        model = PoliceStation
        fields = ['name', 'address', 'contact_number', 'email', 'jurisdiction']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class EmergencyAlertForm(forms.ModelForm):
    class Meta:
        model = EmergencyAlert
        fields = ['title', 'description', 'stations', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'stations': forms.CheckboxSelectMultiple(),
        }