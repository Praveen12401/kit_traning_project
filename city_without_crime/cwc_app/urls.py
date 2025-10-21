# cwc_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('password_reset/', views.user_password_reset, name='password_reset'),
    path('update_password/', views.user_set_new_password, name='update_password'),
    path('registration_by_otp/', views.user_registration_by_otp, name='registration_by_otp'),
    
    # Home
    path('', views.home, name='home'),
    path('profile/', views.user_profile, name='user_profile'),
    
    # Messages
    path('messages/', views.message_list, name='message_list'),
    path('messages/create/', views.create_message, name='create_message'),
    
    # Grievances
    path('grievances/', views.grievance_list, name='grievance_list'),
    path('grievances/create/', views.create_grievance, name='create_grievance'),
    path('grievances/<int:pk>/', views.grievance_detail, name='grievance_detail'),
    path('grievances/<int:pk>/update-status/', views.update_grievance_status, name='update_grievance_status'),
    path('grievances/<int:pk>/feedback/', views.submit_grievance_feedback, name='submit_grievance_feedback'),
    
    # Disciplinary Cases
    path('disciplinary/', views.disciplinary_list, name='disciplinary_list'),
    path('disciplinary/create/', views.create_disciplinary, name='create_disciplinary'),
    path('disciplinary/<int:pk>/', views.disciplinary_detail, name='disciplinary_detail'),
    
    # Faculties
    path('faculties/', views.faculty_list, name='faculty_list'),
    path('faculties/create/', views.create_faculty, name='create_faculty'),
    path('faculties/<int:pk>/', views.faculty_detail, name='faculty_detail'),
    
    # College Alerts
    path('alerts/', views.alert_list, name='alert_list'),
    path('alerts/create/', views.create_alert, name='create_alert'),
    
    # Dashboards
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
]