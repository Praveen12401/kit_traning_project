# management/commands/cleanup_expired_alerts.py
from django.core.management.base import BaseCommand
from django.utils import timezone  # Correct import
from grievance_app.models import CollegeAlert

class Command(BaseCommand):
    help = 'Deactivate expired alerts'
    
    def handle(self, *args, **options):
        expired_count = CollegeAlert.objects.filter(
            is_active=True,
            expires_at__lte=timezone.now()  # Fixed
        ).update(is_active=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deactivated {expired_count} expired alerts')
        )