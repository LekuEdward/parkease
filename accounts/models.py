from django.contrib.auth.models import AbstractUser
from django.db import models

# CustomUser extends Django's AbstractUser with role-based access
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('attendant', 'Parking Attendant'),
        ('manager', 'Section Manager'),
        ('admin', 'System Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='attendant')

    def __str__(self):
        return f"{self.username} — {self.get_role_display()}"

    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    def is_manager(self):
        return self.role == 'manager'

    def is_attendant(self):
        return self.role == 'attendant'
