# cwc_app/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_police = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    station = models.ForeignKey('PoliceStation', on_delete=models.SET_NULL, null=True, blank=True)

class PoliceStation(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    jurisdiction = models.CharField(max_length=100)   
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Criminal(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='criminal_photos/')
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    address = models.TextField()
    crimes = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('WANTED', 'Wanted'),
        ('ARRESTED', 'Arrested'),
        ('RELEASED', 'Released'),
    ])
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('REJECTED', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    station = models.ForeignKey(PoliceStation, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    pincode = models.PositiveIntegerField(blank=True, null=True)
    evidence = models.FileField(upload_to='complaint_evidence/',  null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

class EmergencyAlert(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    stations = models.ManyToManyField(PoliceStation)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

class StationMessage(models.Model):
    sender = models.ForeignKey(PoliceStation, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(PoliceStation, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.subject} - {self.sender} to {self.receiver}"