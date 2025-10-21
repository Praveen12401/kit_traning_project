# cwc_app/views.py
from datetime import timezone
from venv import logger
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import *
from .forms import *
import random, os

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
import smtplib
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

def verify_email_delivery(email_address):
    """
    Verify if email can be delivered by checking MX records and SMTP
    """
    try:
        import dns.resolver
        
        # Extract domain from email
        domain = email_address.split('@')[1]
        
        # Check MX records
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            if not mx_records:
                return False, "Email domain does not exist"
        except:
            return False, "Invalid email domain"
            
        return True, "Email domain is valid"
        
    except ImportError:
        # Fallback if dnspython is not installed
        return True, "Basic validation passed"

def send_simple_email(user_email):
    # Send OTP logic here
    otp = random.randint(100000, 999999)
    user_email = str(user_email)
 
    context = {
        'otp_code': otp,
        'purpose': 'password reset'
    }
    
    # Render HTML template
    text_content = render_to_string('email/otp_email.txt', context)
    
    subject = 'Your Verification Code - College Grievance System'
    try:
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=os.environ.get('EMAIL_HOST_USER'),
            to=[user_email],
            reply_to=['support@collegegrievance.com']
        )
        
        # Validate email format before sending
        from django.core.validators import validate_email
        print(validate_email(user_email))
        
        # Step 2: Verify email delivery capability
        delivery_verified, delivery_message = verify_email_delivery(user_email)
        if not delivery_verified:
            return False, otp

        # Send email
        email.send(fail_silently=False)
        logger.info(f"OTP email sent successfully to {user_email}")
        return True, otp
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        return False, otp

# Authentication Views
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                if user.is_admin:
                    return redirect('admin_dashboard')
                elif user.is_faculty_staff:
                    return redirect('faculty_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
         
        if form.is_valid():
            username = form.cleaned_data['username']
            user_email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            # Session set karna
            request.session['reset_username'] = username
            request.session['reset_email'] = user_email
            request.session['reset_password1'] = password1
            isvalid, otp = send_simple_email(user_email)

            print('user register ',isvalid, otp)
            if isvalid:
                return render(request, 'accounts/registration_by_otp.html', {'otps': otp, 'user_email': user_email})
            else:
                messages.error(request, "Failed to send OTP email. Please check your email address and try again.")
                return render(request, 'accounts/register.html', {'form': form})
        else:
            return render(request, 'accounts/register.html', {'form': form})
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_registration_by_otp(request):
    try:
        # Session se data lo
        username = request.session.get('reset_username')
        user_email = request.session.get('reset_email')
        password1 = request.session.get('reset_password1')
        
        User.objects.create_user(
            username=username,
            email=user_email,
            password=password1,
            is_student=True  # Default student banayein
        )
    except Exception as e:
        print(e)
        messages.error(request, 'Registration failed. Please try again.')
        return redirect('register')
    
    messages.success(request, 'Registration successful! Please login.')
    return redirect('login')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

def user_password_reset(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid(): 
            user_email = form.cleaned_data['email']
             
            # Check if user exists and send OTP
            try:
                if not User.objects.filter(email=user_email).exists():
                    messages.error(request, 'No account found with this email address.')
                    return render(request, 'accounts/password_reset.html', {'form': form})

                isvalid, otp = send_simple_email(user_email)
                # Session set karna
                request.session['reset_email'] = user_email
                 
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
            
            return render(request, 'accounts/confurm_otp_page.html', {'otps': otp, 'user_email': user_email})
    else:
        form = ResetPasswordForm()
    
    return render(request, 'accounts/password_reset.html', {'form': form})

def user_set_new_password(request):
    if request.method == 'POST':
        form = UserSetNewPasswordForm(request.POST)
         
        if form.is_valid():
            new_password = form.cleaned_data['password1']
            confirm_password = form.cleaned_data['password2']
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match')
            try:
                # Session se email lo
                email = request.session.get('reset_email')
                print(email)
                # Sirf usi user ka password update karo jisne request send ki thi
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                
                # Session clear karo
                request.session.flush()
                
                messages.success(request, 'Password updated successfully! Please login.')
                return redirect('login')
            
            except User.DoesNotExist:
                messages.error(request, 'User not found')
        else:
            messages.error(request, 'Something went wrong!')
            return redirect('register')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/set_new_password.html', {'form': form})

# Home Views
def home(request):
    college_alerts = CollegeAlert.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    # Optional: Add dynamic stats
    total_grievances = Grievance.objects.filter(status='RESOLVED').count()
    active_students = User.objects.filter(is_student=True).count()
    
    context = {
        'college_alerts': college_alerts,
        'total_grievances': total_grievances,
        'active_students': active_students,
        'resolution_rate': '95%'  # You can calculate this dynamically
    }
    
    return render(request, 'home/index.html', context)

def message_list(request):
    if not request.user.is_faculty_staff:
        return redirect('home')
    
    faculty = request.user.department
    messages = InterFacultyMessage.objects.filter(
        Q(receiver=faculty) | Q(sender=faculty)
    ).order_by('-created_at')
    
    return render(request, 'dashboard/message_list.html', {'messages': messages})

# Grievance update for faculty and admin
def update_grievance_status(request, pk):
    if not (request.user.is_faculty_staff or request.user.is_admin):
        messages.error(request, "You don't have permission to update grievance status.")
        return redirect('home')
    
    grievance = get_object_or_404(Grievance, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        admin_message = request.POST.get('admin_message')
        
        if new_status in dict(Grievance.STATUS_CHOICES).keys():
            grievance.status = new_status
            grievance.admin_message = admin_message
            if new_status == 'RESOLVED':
                grievance.resolved_at = timezone.now()
            grievance.save()
            messages.success(request, f"Grievance status updated to {grievance.get_status_display()}.")
        else:
            messages.error(request, "Invalid status selected.")
    
    return redirect('grievance_detail', pk=grievance.pk)

# Grievance Views
@login_required
def grievance_list(request):
    if request.user.is_faculty_staff or request.user.is_admin:
        grievances = Grievance.objects.filter(faculty=request.user.department).order_by('-created_at')
    else:
        grievances = Grievance.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'grievances/list.html', {'grievances': grievances})

@login_required
def create_grievance(request):
    if request.method == 'POST':
        form = GrievanceForm(request.POST, request.FILES)
         
        if form.is_valid():
            grievance = form.save(commit=False)
            grievance.user = request.user
            grievance.save()
            messages.success(request, 'Grievance submitted successfully!')
            return redirect('grievance_list')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'grievances/create.html', {'form': form})
    else:
        form = GrievanceForm()
    return render(request, 'grievances/create.html', {'form': form})

@login_required
def grievance_detail(request, pk):
    grievance = get_object_or_404(Grievance, pk=pk)
    if not (request.user == grievance.user or request.user.is_faculty_staff or request.user.is_admin):
        messages.error(request, 'You are not authorized to view this grievance.')
        return redirect('grievance_list')
    
    feedback_form = GrievanceFeedbackForm()
    return render(request, 'grievances/detail.html', {
        'grievance': grievance,
        'feedback_form': feedback_form
    })

@login_required
def submit_grievance_feedback(request, pk):
    grievance = get_object_or_404(Grievance, pk=pk)
    
    if request.user != grievance.user:
        messages.error(request, 'You can only submit feedback for your own grievances.')
        return redirect('grievance_detail', pk=pk)
    
    if request.method == 'POST':
        form = GrievanceFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.grievance = grievance
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
    
    return redirect('grievance_detail', pk=pk)

# Disciplinary Cases Views
@login_required
def disciplinary_list(request):
    if not (request.user.is_faculty_staff or request.user.is_admin):
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('home')
    
    cases = Criminal.objects.all().order_by('-created_at')
    return render(request, 'disciplinary/list.html', {'cases': cases})

@login_required
def create_disciplinary(request):
    if not (request.user.is_faculty_staff or request.user.is_admin):
        messages.error(request, 'You are not authorized to perform this action.')
        return redirect('home')
    
    if request.method == 'POST':
        form = DisciplinaryForm(request.POST, request.FILES)
        if form.is_valid():
            case = form.save(commit=False)
            case.reported_by = request.user
            case.save()
            messages.success(request, 'Disciplinary case added successfully!')
            return redirect('disciplinary_list')
    else:
        form = DisciplinaryForm()
    return render(request, 'disciplinary/create.html', {'form': form})

@login_required
def disciplinary_detail(request, pk):
    case = get_object_or_404(Criminal, pk=pk)
    return render(request, 'disciplinary/detail.html', {'case': case})

# Faculty Views
@login_required
def faculty_list(request):
    faculties = Faculty.objects.all().order_by('faculty_name')
    return render(request, 'faculties/list.html', {'faculties': faculties})

@login_required
def faculty_detail(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    return render(request, 'faculties/detail.html', {'faculty': faculty})

@login_required
def create_faculty(request):
    if not request.user.is_admin:
        messages.error(request, 'You are not authorized to perform this action.')
        return redirect('home')
    
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Faculty added successfully!')
            return redirect('faculty_list')
    else:
        form = FacultyForm()
    return render(request, 'faculties/create.html', {'form': form})

# College Alert Views
@login_required
def alert_list(request):
    alerts = CollegeAlert.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'alerts/list.html', {'alerts': alerts})

@login_required
def create_alert(request):
    if not (request.user.is_faculty_staff or request.user.is_admin):
        messages.error(request, 'You are not authorized to perform this action.')
        return redirect('home')
    
    if request.method == 'POST':
        form = CollegeAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.created_by = request.user
            alert.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'College alert created successfully!')
            return redirect('alert_list')
    else:
        form = CollegeAlertForm()
    return render(request, 'alerts/create.html', {'form': form})

# Inter-Faculty Message Views
@login_required
def create_message(request):
    if not request.user.is_faculty_staff:
        messages.error(request, 'You are not authorized to perform this action.')
        return redirect('home')
    
    if request.method == 'POST':
        form = InterFacultyMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user.department
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('message_list')
    else:
        form = InterFacultyMessageForm()
    return render(request, 'messages/create.html', {'form': form})

# Dashboard Views
@login_required
def admin_dashboard(request):
    if not request.user.is_admin:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('home')
    
    stats = {
        'total_faculties': Faculty.objects.count(),
        'total_grievances': Grievance.objects.count(),
        'pending_grievances': Grievance.objects.filter(status='PENDING').count(),
        'resolved_grievances': Grievance.objects.filter(status='RESOLVED').count(),
        'total_students': User.objects.filter(is_student=True).count(),
        'active_alerts': CollegeAlert.objects.filter(is_active=True).count(),
        'disciplinary_cases': Criminal.objects.count(),
    }
    
    recent_grievances = Grievance.objects.order_by('-created_at')[:5]
    
    return render(request, 'dashboard/admin.html', {
        'stats': stats,
        'recent_grievances': recent_grievances
    })

@login_required
def faculty_dashboard(request):
    if not request.user.is_faculty_staff:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('home')
    
    faculty = request.user.department
    stats = {
        'pending_grievances': Grievance.objects.filter(faculty=faculty, status='PENDING').count(),
        'in_progress_grievances': Grievance.objects.filter(faculty=faculty, status='IN_PROGRESS').count(),
        'resolved_grievances': Grievance.objects.filter(faculty=faculty, status='RESOLVED').count(),
        'unread_messages': InterFacultyMessage.objects.filter(receiver=faculty, is_read=False).count(),
    }
    
    recent_grievances = Grievance.objects.filter(faculty=faculty).order_by('-created_at')[:5]
    
    recent_messages = InterFacultyMessage.objects.filter(
        Q(receiver=faculty) | Q(sender=faculty)
    ).order_by('-created_at')[:3]
    
    active_alerts = CollegeAlert.objects.filter(
        is_active=True,
        target_faculties=faculty
    )
    
    return render(request, 'dashboard/faculty.html', {
        'stats': stats,
        'recent_messages': recent_messages,
        'active_alerts': active_alerts,
        'recent_grievances': recent_grievances
    })

# Profile Views

@login_required
def user_profile(request):
    faculties = Faculty.objects.all()
    
    # Grievance statistics calculate karen
    user_grievances = request.user.grievances.all()
    resolved_count = user_grievances.filter(status='RESOLVED').count()
    pending_count = user_grievances.filter(status='PENDING').count()
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'faculties': faculties,
        'resolved_count': resolved_count,
        'pending_count': pending_count,
        'user_grievances': user_grievances
    })