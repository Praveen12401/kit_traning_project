from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import *

class CustomAdminSite(admin.AdminSite):
    site_header = 'College Grievance System Administration'
    site_title = 'College Grievance System Admin'
    index_title = 'Dashboard'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.admin_dashboard), name='admin_dashboard'),
        ]
        return custom_urls + urls
    
    def admin_dashboard(self, request):
        print("DEBUG: Entered admin_dashboard view")
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

# Create instance of custom admin site
admin_site = CustomAdminSite(name='college_admin')

# Model Admin Classes
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('faculty_name', 'department', 'hod_name', 'contact_number', 'email', 'room_number')
    list_filter = ('faculty_name', 'department')
    search_fields = ('faculty_name', 'department', 'hod_name', 'email')
    ordering = ('faculty_name', 'department')

class GrievanceAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'faculty', 'category', 'priority', 'status', 'created_at')
    list_filter = ('status', 'category', 'priority', 'faculty', 'created_at')
    search_fields = ('title', 'description', 'user__username', 'faculty__faculty_name')
    readonly_fields = ('created_at', 'updated_at', 'resolved_at')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'faculty', 'category', 'title', 'priority')
        }),
        ('Grievance Details', {
            'fields': ('description', 'location', 'supporting_docs', 'photo_evidence')
        }),
        ('Status & Response', {
            'fields': ('status', 'admin_message', 'resolved_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class CriminalAdmin(admin.ModelAdmin):
    list_display = ('name', 'enrollment_number', 'department', 'status', 'reported_by', 'created_at')
    list_filter = ('status', 'department', 'created_at')
    search_fields = ('name', 'enrollment_number', 'issue_description', 'department__faculty_name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Student Information', {
            'fields': ('name', 'enrollment_number', 'department', 'photo')
        }),
        ('Disciplinary Details', {
            'fields': ('issue_description', 'status')
        }),
        ('Reporting Information', {
            'fields': ('reported_by',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class CollegeAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'alert_type', 'created_by', 'is_active', 'created_at')
    list_filter = ('alert_type', 'is_active', 'target_faculties', 'created_at')
    filter_horizontal = ('target_faculties',)
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Alert Information', {
            'fields': ('title', 'alert_type', 'description')
        }),
        ('Target & Duration', {
            'fields': ('target_faculties', 'expires_at', 'is_active')
        }),
        ('Creator Information', {
            'fields': ('created_by',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

class InterFacultyMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'receiver', 'created_at', 'is_read')
    list_filter = ('is_read', 'sender', 'receiver', 'created_at')
    search_fields = ('subject', 'message', 'sender__faculty_name', 'receiver__faculty_name')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

class GrievanceFeedbackAdmin(admin.ModelAdmin):
    list_display = ('grievance', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('grievance__title', 'comments')
    readonly_fields = ('created_at',)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'enrollment_number', 'semester', 'is_student', 'is_faculty_staff', 'is_admin', 'department')
    list_filter = ('is_student', 'is_faculty_staff', 'is_admin', 'is_staff', 'is_superuser', 'department')
    search_fields = ('username', 'email', 'enrollment_number', 'department__faculty_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Information', {
            'fields': ('email', 'enrollment_number', 'semester', 'department')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_student', 'is_faculty_staff', 'is_admin', 'groups', 'user_permissions'),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2', 
                'enrollment_number', 'semester', 'department',
                'is_student', 'is_faculty_staff', 'is_admin'
            ),
        }),
    )

# Register models with the custom admin site
admin_site.register(User, CustomUserAdmin)
admin_site.register(Faculty, FacultyAdmin)
admin_site.register(Grievance, GrievanceAdmin)
admin_site.register(Criminal, CriminalAdmin)
admin_site.register(CollegeAlert, CollegeAlertAdmin)
admin_site.register(InterFacultyMessage, InterFacultyMessageAdmin)
admin_site.register(GrievanceFeedback, GrievanceFeedbackAdmin)

# Replace default admin site
admin.site = admin_site