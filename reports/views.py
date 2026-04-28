from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from parking.models import Vehicle, SignOut
from services.models import ServiceTransaction

# Reports are admin-only — access blocked for attendant and manager roles
@login_required
def dashboard(request):
    if not request.user.is_admin():
        messages.error(request, "Access denied. This page is for System Admins only.")
        return redirect('parking:dashboard')

    date_str = request.GET.get('date', '')
    try:
        from datetime import datetime
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else timezone.now().date()
    except ValueError:
        selected_date = timezone.now().date()

    parking_signouts     = SignOut.objects.filter(sign_out_time__date=selected_date).select_related('vehicle')
    tyre_transactions    = ServiceTransaction.objects.filter(section='tyre',    date=selected_date)
    battery_transactions = ServiceTransaction.objects.filter(section='battery', date=selected_date)

    parking_revenue  = sum(s.fee_charged for s in parking_signouts)
    tyre_revenue     = sum(t.amount for t in tyre_transactions)
    battery_revenue  = sum(t.amount for t in battery_transactions)
    total_revenue    = parking_revenue + tyre_revenue + battery_revenue
    total_vehicles   = Vehicle.objects.filter(arrival_time__date=selected_date).count()

    return render(request, 'reports/dashboard.html', {
        'selected_date':          selected_date,
        'parking_revenue':        parking_revenue,
        'tyre_revenue':           tyre_revenue,
        'battery_revenue':        battery_revenue,
        'total_revenue':          total_revenue,
        'parking_signouts':       parking_signouts,
        'tyre_transactions':      tyre_transactions,
        'battery_transactions':   battery_transactions,
        'total_vehicles':         total_vehicles,
    })
