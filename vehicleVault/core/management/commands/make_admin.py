from django.core.management.base import BaseCommand
from core.models import User


class Command(BaseCommand):
    help = 'Make a user a VehicleVault admin (sets role=admin, is_staff=True, is_admin=True)'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email of the user to promote')

    def handle(self, *args, **options):
        email = options['email']
        try:
            user = User.objects.get(email=email)
            user.role       = 'admin'
            user.is_staff   = True
            user.is_admin   = True
            user.is_active  = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'✅ {email} is now an admin and can access /admin/')
            )
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ No user found with email: {email}'))