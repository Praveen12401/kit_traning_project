# cwc_app/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class Faculty(models.Model):
    faculty_name = models.CharField(max_length=100)  # e.g., "Computer Science", "Mechanical Engineering"
    department = models.CharField(max_length=100)    # e.g., "IT Department", "Mechanical Department"
    hod_name = models.CharField(max_length=100)      # Head of Department
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    room_number = models.CharField(max_length=20, blank=True)  # Faculty room number
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.faculty_name} - {self.department}"

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_student = models.BooleanField(default=True)
    is_faculty_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    # Student/Faculty details
    enrollment_number = models.CharField(max_length=20, blank=True, null=True)  # For students
    semester = models.CharField(max_length=10, blank=True, null=True)  # For students
    department = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

class Grievance(models.Model):  # Complaint ko Grievance rename karen
    CATEGORY_CHOICES = [
        ('ACADEMIC', 'Academic Issue'),
        ('INFRASTRUCTURE', 'Infrastructure Problem'),
        ('FACULTY', 'Faculty Related'),
        ('ADMINISTRATION', 'Administration Issue'),
        ('HOSTEL', 'Hostel Issue'),
        ('LIBRARY', 'Library Issue'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('UNDER_REVIEW', 'Under Review'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('REJECTED', 'Rejected'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grievances')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, verbose_name="Related Faculty/Department")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    title = models.CharField(max_length=200, verbose_name="Grievance Title")
    description = models.TextField(max_length=1000, verbose_name="Detailed Description")
    location = models.CharField(max_length=200, verbose_name="Location/Place of Issue")  # branch -> location
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    
    # Evidence/Attachments
    supporting_docs = models.FileField(
        upload_to='grievance_documents/', 
        null=True, 
        blank=True,
        verbose_name="Supporting Documents"
    )
    photo_evidence = models.ImageField(
        upload_to='grievance_photos/', 
        null=True, 
        blank=True,
        verbose_name="Photo Evidence"
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    admin_message = models.CharField(max_length=500, blank=True, null=True, verbose_name="Admin Response")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

class Criminal(models.Model):  # Isko StudentDisciplinary ya kuch aur rename kar sakte hain
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='disciplinary_photos/', blank=True, null=True)
    enrollment_number = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)
    issue_description = models.TextField(verbose_name="Disciplinary Issue")  # crimes -> issue_description
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending Review'),
        ('UNDER_INVESTIGATION', 'Under Investigation'),
        ('RESOLVED', 'Resolved'),
        ('WARNING_ISSUED', 'Warning Issued'),
    ], default='PENDING')
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class CollegeAlert(models.Model):  # EmergencyAlert -> CollegeAlert
    ALERT_TYPES = [
        ('ACADEMIC', 'Academic Alert'),
        ('EMERGENCY', 'Emergency Alert'),
        ('GENERAL', 'General Notice'),
        ('EVENT', 'Event Announcement'),
    ]
    
    title = models.CharField(max_length=200)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, default='GENERAL')
    description = models.TextField()
    target_faculties = models.ManyToManyField(Faculty, verbose_name="Target Faculties/Departments")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.get_alert_type_display()}: {self.title}"

class InterFacultyMessage(models.Model):  # StationMessage -> InterFacultyMessage
    sender = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.subject} - {self.sender} to {self.receiver}"

class GrievanceFeedback(models.Model):
    grievance = models.OneToOneField(Grievance, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    comments = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback for {self.grievance.title}"