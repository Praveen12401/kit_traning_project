# utils.py
import random
from django.core.cache import cache
from django.core.mail import send_mail

from city_without_crime.city_without_crime import settings

def generate_and_send_otp(email):
    otp = random.randint(100000, 999999)
    
    # OTP cache mein store karein (5 minutes)
    cache.set(f'otp_{email}', otp, 300)
    
    # Email send karein
    subject = 'OTP for Grievance System Login'
    message = f'Your OTP is: {otp}. Valid for 5 minutes.'
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
    
    return otp