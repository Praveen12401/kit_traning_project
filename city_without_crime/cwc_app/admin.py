from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import *

class CustomAdminSite(admin.AdminSite):
    site_header = 'City Without Crime Administration'
    site_title = 'City Without Crime Admin'
    index_title = 'Dashboard'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.admin_dashboard), name='admin_dashboard'),
        ]
        return custom_urls + urls
    
    def admin_dashboard(self, request):
        print("DEBUG: Entered admin_dashboard view")  # Add this line
        stats = {
            'total_stations': PoliceStation.objects.count(),
            'total_complaints': Complaint.objects.count(),
            'total_criminals': Criminal.objects.count(),
            'active_alerts': EmergencyAlert.objects.filter(is_active=True).count(),
             
        }
        recent_complaints = Complaint.objects.order_by('-created_at')[:5]
        return render(request, 'dashboard/admin.html', {'stats':stats,'recent_complaints':recent_complaints})

# Create instance of custom admin site
admin_site = CustomAdminSite(name='cwc_admin')

# Model Admin Classes
class PoliceStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'jurisdiction', 'contact_number', 'email')
    list_filter = ('jurisdiction',)
    search_fields = ('name', 'jurisdiction', 'contact_number')
    ordering = ('name',)

class CriminalAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'gender', 'status', 'added_by', 'created_at')
    list_filter = ('status', 'gender', 'added_by')
    search_fields = ('name', 'crimes', 'address')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {'fields': ('name', 'photo', 'age', 'gender')}),
        ('Details', {'fields': ('address', 'crimes', 'status')}),
        ('Metadata', {
            'fields': ('added_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'station', 'status', 'created_at')
    list_filter = ('status', 'station', 'created_at')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {'fields': ('user', 'station', 'title')}),
        ('Details', {'fields': ('description', 'location','pincode', 'evidence')}),
        ('Status', {'fields': ('status',)}),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'is_active', 'created_at')
    list_filter = ('is_active', 'stations')
    filter_horizontal = ('stations',)
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

class StationMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'receiver', 'created_at', 'is_read')
    list_filter = ('is_read', 'sender', 'receiver')
    search_fields = ('subject', 'message')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_police', 'is_admin', 'station')
    list_filter = ('is_police', 'is_admin', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'station__name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_police', 'is_admin', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Station Info', {'fields': ('station',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_police', 'is_admin', 'station'),
        }),
    )

# Register models with the custom admin site
admin_site.register(User, CustomUserAdmin)
admin_site.register(PoliceStation, PoliceStationAdmin)
admin_site.register(Criminal, CriminalAdmin)
admin_site.register(Complaint, ComplaintAdmin)
admin_site.register(EmergencyAlert, EmergencyAlertAdmin)
admin_site.register(StationMessage, StationMessageAdmin)

# Replace default admin site
admin.site = admin_site