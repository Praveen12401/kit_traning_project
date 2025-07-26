# cwc_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    # Home
    path('', views.home, name='home'),
    
    # Complaints
    path('complaints/', views.complaint_list, name='complaint_list'),
    path('complaints/create/', views.create_complaint, name='create_complaint'),
    path('complaints/<int:pk>/', views.complaint_detail, name='complaint_detail'),
    
    # Criminals
    path('criminals/', views.criminal_list, name='criminal_list'),
    path('criminals/create/', views.create_criminal, name='create_criminal'),
    path('criminals/<int:pk>/', views.criminal_detail, name='criminal_detail'),
    
    # Police Stations
    path('stations/', views.station_list, name='station_list'),
    path('stations/create/', views.create_station, name='create_station'),
    
    # Emergency
    path('emergency/', views.emergency_list, name='emergency_list'),
    path('emergency/create/', views.create_emergency, name='create_emergency'),
    
    # Dashboards
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('police/dashboard/', views.police_dashboard, name='police_dashboard'),
]

