# cwc_app/views.py
from venv import logger
from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import *
from .forms import *
import random,os

from django.core.mail import send_mail,EmailMultiAlternatives
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
    user_email=str(user_email)
 
    context = {
             
            'otp_code': otp,
            'purpose': 'password reset'
        }
     # Render HTML template
    text_content = render_to_string('email/otp_email.txt', context)
    # Email subject based on purpose
     
    subject =  'Your Verification Code - City Without Crime'
    try:
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email= os.environ.get('EMAIL_HOST_USER') ,
            to=[user_email],
            reply_to=['support@yourplatform.com']
        )
        
        # Validate email format before sending
        from django.core.validators import validate_email
        print(validate_email(user_email))
        # Step 2: Verify email delivery capability
        delivery_verified, delivery_message = verify_email_delivery(user_email)
        if not delivery_verified:
            return False,otp 

        # Send email
        email.send(fail_silently=False)
        logger.info(f"OTP email sent successfully to {user_email}")
        return True,otp
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        return False,otp
    

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
                messages.success(request, f'Welcome back, {username}!')  # Add this line
                if user.is_admin:
                    return redirect('admin_dashboard')
                elif user.is_police:
                    return redirect('police_dashboard')
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
            username=form.cleaned_data['username']
            user_email=form.cleaned_data['email']
            password1=form.cleaned_data['password1']
            # Session set karna
            request.session['reset_username'] = username
            request.session['reset_email'] = user_email
            request.session['reset_password1'] = password1
            isvalid,otp =send_simple_email(user_email)

            print(isvalid,otp)
            if isvalid:
            # print('otp sent')
                return  render(request,'accounts/registration_by_otp.html',{'otps':otp,'user_email':user_email})
            else:
                messages.error(request,"Failed to send OTP email. Please check your email address and try again.")
                return render(request, 'accounts/register.html', {'form': form})


            # user = form.save()
            # login(request, user)
            
        else:
             
            return render(request, 'accounts/register.html', {'form': form})
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})
''' after registration form fill and submit and otp varifyed then
 this function run and user create'''
def user_registration_by_otp(request):
    try:
        # Session se email lo
        username = request.session.get('reset_username')
        user_email = request.session.get('reset_email')
        password1 = request.session.get('reset_password1')
        User.objects.create_user(
                username=username,
                email=user_email,
                password=password1,
                
            )
    except Exception as e:
        print(e)
    messages.success(request, 'Registration successful! now login')
    return redirect('login')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')
 
def user_password_reset(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid(): 
            user_email=form.cleaned_data['email']
             
            # Check if user exists and send OTP
            try:
                if not User.objects.filter(email=user_email).exists():
                    messages.error(request, 'No account found with this email address.')

                    return render(request,'accounts/password_reset.html',{'form':form})

                
                isvalid,otp=send_simple_email(user_email)
                # Session set karna
                request.session['reset_email'] = user_email
                 
                 
            
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')

            
            return  render(request,'accounts/confurm_otp_page.html',{'otps':otp,'user_email':user_email})

    else:
        form = ResetPasswordForm()
     
    
    return render(request,'accounts/password_reset.html',{'form':form})

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
                
                messages.success(request, 'Password updated successfully now login!')
                return redirect('login')
            
            except User.DoesNotExist:
                messages.error(request, 'User not found')
        else:
            messages.error(request, 'Wrong something!')
            return redirect('register')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/set_new_password.html', {'form': form})


# Home Views
def home(request):
    emergency_alerts = EmergencyAlert.objects.filter(is_active=True).order_by('-created_at')[:5]
    return render(request, 'home/index.html', {'emergency_alerts': emergency_alerts})

def message_list(request):
    if not request.user.is_police:
        return redirect('home')
    
    station = request.user.station
    message = StationMessage.objects.filter(
        Q(receiver=station) | Q(sender=station)
    ).order_by('-created_at')
    
    return render(request, 'dashboard/message_list.html', {'message': message})
# complaint update for police and admin
def update_complaint_status(request, pk):
    if not request.user.is_police:
        messages.error(request, "You don't have permission to update complaint status.")
        return redirect('home')
    
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        new_message = request.POST.get('message')
        
        if new_status in dict(Complaint.STATUS_CHOICES).keys():
            complaint.status = new_status
            complaint.message = new_message
            complaint.save()
            messages.success(request, f"Complaint status updated to {complaint.get_status_display()}.")
        else:
            messages.error(request, "Invalid status selected.")
    
    return redirect('complaint_detail', pk=complaint.pk)

# Complaint Views
@login_required
def complaint_list(request):
    if request.user.is_police or request.user.is_admin:
        complaints = Complaint.objects.filter(station=request.user.station).order_by('-created_at')
         
    else:
        complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
        print(complaints)
    return render(request, 'complaints/list.html', {'complaints': complaints})

@login_required
def create_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
         
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            messages.success(request, 'Complaint submitted successfully!')
            return redirect('complaint_list')
        else:
            messages.error(request, 'Complaint not correct fill please')
            return redirect('complaint_list')

    else:
        
        form = ComplaintForm()
    return render(request, 'complaints/create.html', {'form': form})

@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if not (request.user == complaint.user or request.user.is_police or request.user.is_admin):
        messages.error(request, 'You are not authorized to view this complaint.')
        return redirect('complaint_list')
    return render(request, 'complaints/detail.html', {'complaint': complaint})

# Criminal Views
@login_required
def criminal_list(request):
    criminals = Criminal.objects.all().order_by('-created_at')
    return render(request, 'criminals/list.html', {'criminals': criminals})

@login_required
def create_criminal(request):
    if not (request.user.is_police or request.user.is_admin):
        messages.error(request, 'You are not authorized to perform this action.')
        return redirect('home')
    
    if request.method == 'POST':
        form = CriminalForm(request.POST, request.FILES)
        if form.is_valid():
            criminal = form.save(commit=False)
            criminal.added_by = request.user
            criminal.save()
            messages.success(request, 'Criminal record added successfully!')
            return redirect('criminal_list')
    else:
        form = CriminalForm()
    return render(request, 'criminals/create.html', {'form': form})

@login_required
def criminal_detail(request, pk):
    criminal = get_object_or_404(Criminal, pk=pk)
    return render(request, 'criminals/detail.html', {'criminal': criminal})

# Police Station Views
@login_required
def station_list(request):
    stations = PoliceStation.objects.all().order_by('name')
    return render(request, 'police_stations/list.html', {'stations': stations})

@login_required
def station_detail(request, pk):
    station = get_object_or_404(PoliceStation, pk=pk)
    return render(request, 'police_stations/detail.html', {'station': station})

@login_required
def create_station(request):
    if not request.user.is_admin:
        messages.error(request, 'You are not authorized to perform this action.')
        return redirect('home')
    
    if request.method == 'POST':
        form = PoliceStationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Police station added successfully!')
            return redirect('station_list')
    else:
        form = PoliceStationForm()
    return render(request, 'police_stations/create.html', {'form': form})

# Emergency Views
@login_required
def emergency_list(request):
    alerts = EmergencyAlert.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'emergency/list.html', {'alerts': alerts})

@login_required
def create_emergency(request):
    if not (request.user.is_police or request.user.is_admin):
        messages.error(request, 'You are not authorized to perform this action.')
        return redirect('home')
    
    if request.method == 'POST':
        form = EmergencyAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.created_by = request.user
            alert.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Emergency alert created successfully!')
            return redirect('emergency_list')
    else:
        form = EmergencyAlertForm()
    return render(request, 'emergency/create.html', {'form': form})

   




@login_required
def admin_dashboard(request):
    print("DEBUG: Entered admin_dashboard view")  # Add this line
    if not request.user.is_admin:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('home')
    
    stats = {
        'total_stations': PoliceStation.objects.count(),
        'total_complaints': Complaint.objects.count(),
        'total_criminals': Criminal.objects.count(),
        'active_alerts': EmergencyAlert.objects.filter(is_active=True).count(),
    }
    print(stats,'ram')
    
    recent_complaints = Complaint.objects.order_by('-created_at')[:5]
    
    return render(request, 'dashboard/admin.html', {
        'stats': stats,
        'recent_complaints': recent_complaints
    })
   
@login_required
def police_dashboard(request):
    
    if not request.user.is_police:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('home')
    
    station = request.user.station
    stats = {
        'pending_complaints': Complaint.objects.filter(station=station, status='PENDING').count(),
        'in_progress_complaints': Complaint.objects.filter(station=station, status='IN_PROGRESS').count(),
        'resolved_complaints': Complaint.objects.filter(station=station, status='RESOLVED').count(),
        'unread_messages': StationMessage.objects.filter(receiver=station, is_read=False).count(),
    }
  
    recent_complaints = Complaint.objects.order_by('-created_at')[:5]
    
    recent_messages = StationMessage.objects.filter(
        Q(receiver=station) | Q(sender=station)
    ).order_by('-created_at')[:3]
    
    active_alerts = EmergencyAlert.objects.filter(
        is_active=True,
        stations=station
    )
    
    return render(request, 'dashboard/police.html', {
        'stats': stats,
        'recent_messages': recent_messages,
        'active_alerts': active_alerts,
        'recent_complaints':recent_complaints
    })