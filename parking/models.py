from django.db import models
from django.utils import timezone


# Vehicle stores all registration data captured on arrival
class Vehicle(models.Model):
    """A vehicle registered on arrival at the parking facility."""

    VEHICLE_TYPES = [
        ('personal_car', 'Personal Car'),
        ('taxi', 'Taxi'),
        ('truck', 'Truck'),
        ('coaster', 'Coaster'),
        ('boda_boda', 'Boda-boda'),
    ]

    driver_name    = models.CharField(max_length=100)
    vehicle_type   = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    plate_number   = models.CharField(max_length=10)
    model_color    = models.CharField(max_length=100, help_text="e.g. Toyota Harrier, Silver")
    phone          = models.CharField(max_length=15)
    nin            = models.CharField(max_length=20, blank=True, help_text="Required for Boda-boda only")
    arrival_time   = models.DateTimeField(default=timezone.now)
    is_signed_out  = models.BooleanField(default=False)
    registered_by  = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.plate_number} — {self.driver_name}"


class SignOut(models.Model):
    """Recorded when a vehicle leaves the facility."""

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    vehicle         = models.OneToOneField(Vehicle, on_delete=models.CASCADE)
    receiver_name   = models.CharField(max_length=100)
    receiver_phone  = models.CharField(max_length=15)
    receiver_gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    receiver_nin    = models.CharField(max_length=20)
    sign_out_time   = models.DateTimeField(default=timezone.now)
    fee_charged     = models.DecimalField(max_digits=10, decimal_places=2)
    rate_category   = models.CharField(max_length=10)   # 'day', 'night', or 'short'
    receipt_number  = models.CharField(max_length=30, unique=True, blank=True)

    def __str__(self):
        return f"Receipt {self.receipt_number} — {self.vehicle.plate_number}"

    def save(self, *args, **kwargs):
        # Auto-generate receipt number on first save
        if not self.receipt_number:
            from datetime import date
            today = date.today().strftime('%Y%m%d')
            count = SignOut.objects.filter(sign_out_time__date=date.today()).count()
            self.receipt_number = f"PRK-{today}-{str(count + 1).zfill(4)}"
        super().save(*args, **kwargs)

    def duration_hours(self):
        """Returns hours parked, rounded to 1 decimal place."""
        diff = self.sign_out_time - self.vehicle.arrival_time
        return round(diff.total_seconds() / 3600, 1)
