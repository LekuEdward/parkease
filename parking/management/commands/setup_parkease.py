"""
Run this once after every fresh installation:
    python manage.py setup_parkease
"""
from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from services.models import ServicePrice


class Command(BaseCommand):
    help = 'Creates all default ParkEase users and service prices'

    def handle(self, *args, **kwargs):

        # ── 1. Users ──────────────────────────────────────
        users = [
            dict(username='admin',     password='admin123',
                 first_name='Alex',    last_name='Mukasa',
                 role='admin',         email='admin@parkease.ug',
                 is_staff=True,        is_superuser=True),
            dict(username='attendant', password='park2026',
                 first_name='Grace',   last_name='Namutebi',
                 role='attendant',     email='attendant@parkease.ug'),
            dict(username='manager',   password='mgr2026',
                 first_name='David',   last_name='Ssekitoleko',
                 role='manager',       email='manager@parkease.ug'),
        ]

        for u in users:
            password = u.pop('password')
            obj, created = CustomUser.objects.get_or_create(
                username=u['username'], defaults=u
            )
            if created:
                obj.set_password(password)
                obj.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✅ Created user: {obj.username} "
                        f"({obj.get_role_display()}) — password: {password}"
                    )
                )
            else:
                # Always reset the password so it works even if db existed
                obj.set_password(password)
                for key, val in u.items():
                    setattr(obj, key, val)
                obj.save()
                self.stdout.write(
                    self.style.WARNING(
                        f"  🔄 Reset user: {obj.username} — password: {password}"
                    )
                )

        # ── 2. Service Prices ──────────────────────────────
        prices = [
            ('tyre_pressure', 500),
            ('tyre_puncture', 5000),
            ('tyre_valve',    5000),
            ('battery_hire',  20000),
            ('battery_sale',  150000),
        ]

        for service_type, price in prices:
            obj, created = ServicePrice.objects.get_or_create(
                service_type=service_type,
                defaults={'price': price}
            )
            label = obj.get_service_type_display()
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ Created price: {label} — UGX {price:,}")
                )
            else:
                self.stdout.write(f"  — Price already exists: {label}")

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('ParkEase setup complete!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')
        self.stdout.write('  Login details:')
        self.stdout.write('    admin      / admin123  (System Admin)')
        self.stdout.write('    attendant  / park2026  (Parking Attendant)')
        self.stdout.write('    manager    / mgr2026   (Section Manager)')
        self.stdout.write('')
