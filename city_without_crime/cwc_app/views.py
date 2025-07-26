# cwc_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import *

# Authentication Views
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            print(user)
            if user is not None:
                login(request, user)
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
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
        else:
            messages.error(request, 'Wrong something!')
            return redirect('register')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

# Home Views
def home(request):
    emergency_alerts = EmergencyAlert.objects.filter(is_active=True).order_by('-created_at')[:5]
    return render(request, 'home/index.html', {'emergency_alerts': emergency_alerts})

# Complaint Views
@login_required
def complaint_list(request):
    if request.user.is_police or request.user.is_admin:
        complaints = Complaint.objects.filter(station=request.user.station).order_by('-created_at')
    else:
        complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
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

# Dashboard Views
@login_required
def admin_dashboard(request):
    if not request.user.is_admin:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('home')
    
    stats = {
        'total_stations': PoliceStation.objects.count(),
        'total_complaints': Complaint.objects.count(),
        'total_criminals': Criminal.objects.count(),
        'active_alerts': EmergencyAlert.objects.filter(is_active=True).count(),
    }
    return render(request, 'dashboard/admin.html', {'stats': stats})

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
    return render(request, 'dashboard/police.html', {'stats': stats})