from django.contrib import admin
from .models import Vehicle, SignOut

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['plate_number', 'driver_name', 'vehicle_type', 'arrival_time', 'is_signed_out']
    list_filter  = ['vehicle_type', 'is_signed_out']
    search_fields = ['plate_number', 'driver_name']

@admin.register(SignOut)
class SignOutAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'vehicle', 'fee_charged', 'rate_category', 'sign_out_time']
