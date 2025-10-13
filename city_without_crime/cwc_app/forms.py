# cwc_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from pydantic import ValidationError
from .models import *

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please use a different email.")
        
        return email

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

# ✅ Naya form sirf reset password ke liye
class ResetPasswordForm(forms.Form):
    email = forms.EmailField(required=True, label="Enter your email")

class UserSetNewPasswordForm(UserCreationForm):
     
    
    class Meta:
        model = User
        fields = [ 'password1', 'password2']
    
     

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint    
        fields = ['station', 'title', 'description', 'location','pincode', 'evidence']
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