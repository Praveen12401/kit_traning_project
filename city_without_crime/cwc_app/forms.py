# cwc_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    enrollment_number = forms.CharField(max_length=20, required=False, help_text="For students only")
    semester = forms.CharField(max_length=10, required=False, help_text="For students only")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'enrollment_number', 'semester', 'department', 'password1', 'password2']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please use a different email.")
        
        return email

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your password'
    }))

class ResetPasswordForm(forms.Form):
    email = forms.EmailField(
        required=True, 
        label="Enter your email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registered email'
        })
    )

class UserSetNewPasswordForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['password1', 'password2']

class GrievanceForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ['faculty', 'category', 'title', 'description', 'location', 'priority', 'supporting_docs', 'photo_evidence']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 6, 
                'class': 'form-control',
                'placeholder': 'Describe your grievance in detail...',
                'style': 'resize: vertical; min-height: 150px;'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a brief title for your grievance'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Where did this issue occur? (e.g., Room No, Building Name)'
            }),
            'faculty': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'faculty': 'Select Faculty/Department',
            'location': 'Location of Issue',
            'supporting_docs': 'Supporting Documents (if any)',
            'photo_evidence': 'Photo Evidence (if any)',
        }

class GrievanceUpdateForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ['status', 'admin_message']
        widgets = {
            'admin_message': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Enter response or update for the student...',
                'style': 'resize: vertical; min-height: 100px;'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class DisciplinaryForm(forms.ModelForm):
    class Meta:
        model = Criminal
        fields = ['name', 'enrollment_number', 'department', 'photo', 'issue_description', 'status']
        widgets = {
            'issue_description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Describe the disciplinary issue...',
                'style': 'resize: vertical; min-height: 120px;'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter student name'
            }),
            'enrollment_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter enrollment number'
            }),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'issue_description': 'Disciplinary Issue Description',
        }

class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['faculty_name', 'department', 'hod_name', 'contact_number', 'email', 'room_number']
        widgets = {
            'faculty_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Computer Science'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., IT Department'
            }),
            'hod_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Head of Department name'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Department email'
            }),
            'room_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Room number (optional)'
            }),
        }

class CollegeAlertForm(forms.ModelForm):
    class Meta:
        model = CollegeAlert
        fields = ['title', 'alert_type', 'description', 'target_faculties', 'expires_at', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Enter alert description...',
                'style': 'resize: vertical; min-height: 120px;'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter alert title'
            }),
            'alert_type': forms.Select(attrs={'class': 'form-control'}),
            'target_faculties': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
        labels = {
            'target_faculties': 'Target Faculties/Departments',
            'expires_at': 'Expiry Date & Time (optional)',
        }

# forms.py
class InterFacultyMessageForm(forms.ModelForm):
    class Meta:
        model = InterFacultyMessage
        fields = ['receiver', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Type your message...',
                'style': 'resize: vertical; min-height: 150px;'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter message subject'
            }),
            'receiver': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Filter receivers to exclude the current user's department
        if self.request and self.request.user.department:
            self.fields['receiver'].queryset = Faculty.objects.exclude(id=self.request.user.department.id)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.request and self.request.user.department:
            instance.sender = self.request.user.department
        if commit:
            instance.save()
        return instance

class GrievanceFeedbackForm(forms.ModelForm):
    class Meta:
        model = GrievanceFeedback
        fields = ['rating', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Share your feedback about grievance resolution... (optional)',
                'style': 'resize: vertical; min-height: 100px;'
            }),
            'rating': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'rating': 'Rate your satisfaction (1-5)',
            'comments': 'Additional Comments',
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'enrollment_number', 'semester', 'department']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'enrollment_number': forms.TextInput(attrs={'class': 'form-control'}),
            'semester': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
        }