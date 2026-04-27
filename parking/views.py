from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Vehicle, SignOut
from .forms import VehicleRegistrationForm, VehicleEditForm, SignOutForm, VehicleSearchForm
from services.models import ServiceTransaction


PARKING_RATES = {
    'personal_car': {'day': 3000,  'night': 2000,  'short': 2000},
    'taxi':         {'day': 3000,  'night': 2000,  'short': 2000},
    'truck':        {'day': 5000,  'night': 10000, 'short': 2000},
    'coaster':      {'day': 4000,  'night': 2000,  'short': 3000},
    'boda_boda':    {'day': 2000,  'night': 2000,  'short': 1000},
}
RATE_LABELS = {
    'day':   'Day Rate (6:00 am – 6:59 pm)',
    'night': 'Night Rate (7:00 pm – 5:59 am)',
    'short': 'Short Stay (under 3 hours)',
}


def calculate_fee(vehicle_type, arrival_time, departure_time):
    duration    = departure_time - arrival_time
    hours       = duration.total_seconds() / 3600
    depart_hour = departure_time.hour
    if hours < 3:
        category = 'short'
    elif 6 <= depart_hour <= 18:
        category = 'day'
    else:
        category = 'night'
    return PARKING_RATES.get(vehicle_type, {}).get(category, 0), category


@login_required
def dashboard(request):
    today = timezone.now().date()

    # ── Parking stats (for attendants and admins) ──
    currently_parked = Vehicle.objects.filter(is_signed_out=False)
    signed_out_today = SignOut.objects.filter(sign_out_time__date=today)
    parking_revenue  = sum(s.fee_charged for s in signed_out_today)
    recent_arrivals  = currently_parked.order_by('-arrival_time')[:8]

    # ── Services stats (for managers and admins) ──
    tyre_today    = ServiceTransaction.objects.filter(section='tyre',    date=today)
    battery_today = ServiceTransaction.objects.filter(section='battery', date=today)
    tyre_revenue  = sum(t.amount for t in tyre_today)
    battery_rev   = sum(t.amount for t in battery_today)

    return render(request, 'parking/dashboard.html', {
        'parked':           currently_parked.count(),
        'signed_out':       signed_out_today.count(),
        'parking_revenue':  parking_revenue,
        'recent_arrivals':  recent_arrivals,
        'today':            today,
        'tyre_today':       tyre_today.count(),
        'battery_today':    battery_today.count(),
        'tyre_revenue':     tyre_revenue,
        'battery_revenue':  battery_rev,
        'total_revenue':    parking_revenue + tyre_revenue + battery_rev,
    })


@login_required
def vehicle_list(request):
    vehicles = Vehicle.objects.filter(is_signed_out=False).order_by('-arrival_time')
    return render(request, 'parking/vehicle_list.html', {'vehicles': vehicles})


@login_required
def register_vehicle(request):
    if request.method == 'POST':
        form = VehicleRegistrationForm(request.POST)
        if form.is_valid():
            vehicle               = form.save(commit=False)
            vehicle.registered_by = request.user
            vehicle.save()
            messages.success(
                request,
                f"✅ Vehicle {vehicle.plate_number} registered! "
                f"Arrival: {vehicle.arrival_time.strftime('%I:%M %p')}"
            )
            return redirect('parking:dashboard')
    else:
        form = VehicleRegistrationForm()
    return render(request, 'parking/register.html', {'form': form})


@login_required
def edit_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, is_signed_out=False)
    if request.method == 'POST':
        form = VehicleEditForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Vehicle {vehicle.plate_number} updated.")
            return redirect('parking:vehicle_list')
    else:
        form = VehicleEditForm(instance=vehicle)
    return render(request, 'parking/edit_vehicle.html', {'form': form, 'vehicle': vehicle})


@login_required
def delete_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, is_signed_out=False)
    if request.method == 'POST':
        plate = vehicle.plate_number
        vehicle.delete()
        messages.success(request, f"🗑 Vehicle {plate} removed from the system.")
        return redirect('parking:vehicle_list')
    return render(request, 'parking/delete_vehicle.html', {'vehicle': vehicle})


@login_required
def signout_search(request):
    form    = VehicleSearchForm(request.GET or None)
    vehicle = None
    error   = None
    if request.GET.get('search'):
        search  = request.GET.get('search', '').strip().upper().replace(' ', '')
        vehicle = Vehicle.objects.filter(plate_number=search, is_signed_out=False).first()
        if not vehicle:
            already = SignOut.objects.filter(vehicle__plate_number=search).first()
            if already:
                error = f"Vehicle {search} has already been signed out (Receipt: {already.receipt_number})."
            else:
                error = f"No active vehicle found for '{search}'. Check the plate number."
    return render(request, 'parking/signout_search.html', {
        'form': form, 'vehicle': vehicle, 'error': error,
    })


@login_required
def signout_process(request, pk):
    vehicle          = get_object_or_404(Vehicle, pk=pk, is_signed_out=False)
    now              = timezone.now()
    fee, category    = calculate_fee(vehicle.vehicle_type, vehicle.arrival_time, now)
    hours            = round((now - vehicle.arrival_time).total_seconds() / 3600, 1)
    rate_label       = RATE_LABELS.get(category, category)

    if request.method == 'POST':
        form = SignOutForm(request.POST)
        if form.is_valid():
            signout               = form.save(commit=False)
            signout.vehicle       = vehicle
            signout.sign_out_time = now
            signout.fee_charged   = fee
            signout.rate_category = category
            signout.save()
            vehicle.is_signed_out = True
            vehicle.save()
            messages.success(
                request,
                f"✅ {vehicle.plate_number} signed out. Fee: UGX {fee:,}. Receipt: {signout.receipt_number}"
            )
            return redirect('parking:receipt', receipt_number=signout.receipt_number)
    else:
        form = SignOutForm()

    return render(request, 'parking/signout_process.html', {
        'vehicle': vehicle, 'fee': fee, 'category': category,
        'rate_label': rate_label, 'hours': hours, 'form': form, 'now': now,
    })


@login_required
def receipt_view(request, receipt_number):
    signout = get_object_or_404(SignOut, receipt_number=receipt_number)
    return render(request, 'parking/receipt.html', {'signout': signout})


@login_required
def history(request):
    signouts = SignOut.objects.select_related('vehicle').order_by('-sign_out_time')
    total    = sum(s.fee_charged for s in signouts)
    return render(request, 'parking/history.html', {'signouts': signouts, 'total': total})
