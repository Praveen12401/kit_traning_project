from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

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
        (None, {
            'fields': ('name', 'photo', 'age', 'gender')
        }),
        ('Details', {
            'fields': ('address', 'crimes', 'status')
        }),
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
        (None, {
            'fields': ('user', 'station', 'title')
        }),
        ('Details', {
            'fields': ('description', 'location', 'evidence')
        }),
        ('Status', {
            'fields': ('status',)
        }),
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

# Register your models here
admin.site.register(User, CustomUserAdmin)
admin.site.register(PoliceStation, PoliceStationAdmin)
admin.site.register(Criminal, CriminalAdmin)
admin.site.register(Complaint, ComplaintAdmin)
admin.site.register(EmergencyAlert, EmergencyAlertAdmin)
admin.site.register(StationMessage, StationMessageAdmin)