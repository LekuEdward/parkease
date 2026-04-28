from django.db import models
from django.utils import timezone

# ServicePrice stores tyre and battery prices set by the Section Manager
class ServicePrice(models.Model):
    """Prices for tyre and battery services — set by the Section Manager."""

    SERVICE_CHOICES = [
        ('tyre_pressure',  'Tyre Pressure Check'),
        ('tyre_puncture',  'Puncture Fixing'),
        ('tyre_valve',     'Tyre Valve Replacement'),
        ('battery_hire',   'Battery Hire'),
        ('battery_sale',   'Battery Sale'),
    ]

    service_type = models.CharField(max_length=30, choices=SERVICE_CHOICES, unique=True)
    price        = models.DecimalField(max_digits=10, decimal_places=2)
    updated_by   = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True
    )
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_service_type_display()} — UGX {self.price:,.0f}"


class ServiceTransaction(models.Model):
    """A single tyre or battery service transaction."""

    SECTION_CHOICES = [
        ('tyre',    'Tyre Clinic'),
        ('battery', 'Battery Section'),
    ]

    section       = models.CharField(max_length=10, choices=SECTION_CHOICES)
    service       = models.ForeignKey(ServicePrice, on_delete=models.SET_NULL, null=True)
    customer_name = models.CharField(max_length=100)
    phone         = models.CharField(max_length=15)
    amount        = models.DecimalField(max_digits=10, decimal_places=2)
    date          = models.DateField(default=timezone.now)
    receipt_number = models.CharField(max_length=30, unique=True, blank=True)
    recorded_by   = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.receipt_number} — {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            from datetime import date
            prefix = 'TYR' if self.section == 'tyre' else 'BAT'
            today  = date.today().strftime('%Y%m%d')
            count  = ServiceTransaction.objects.filter(
                section=self.section, date=date.today()
            ).count()
            self.receipt_number = f"{prefix}-{today}-{str(count + 1).zfill(4)}"
        super().save(*args, **kwargs)
