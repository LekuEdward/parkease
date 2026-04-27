from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ServicePrice, ServiceTransaction
from .forms import ServicePriceForm, TyreTransactionForm, BatteryTransactionForm


@login_required
def price_list(request):
    prices = ServicePrice.objects.all()
    return render(request, 'services/price_list.html', {'prices': prices})


@login_required
def set_price(request, pk=None):
    if not (request.user.is_manager() or request.user.is_admin()):
        messages.error(request, "Access denied. Managers only.")
        return redirect('services:price_list')

    instance = get_object_or_404(ServicePrice, pk=pk) if pk else None
    if request.method == 'POST':
        form = ServicePriceForm(request.POST, instance=instance)
        if form.is_valid():
            price = form.save(commit=False)
            price.updated_by = request.user
            price.save()
            messages.success(request, 'Service price saved!')
            return redirect('services:price_list')
    else:
        form = ServicePriceForm(instance=instance)
    return render(request, 'services/price_form.html', {'form': form, 'title': 'Set Service Price'})


@login_required
def tyre_list(request):
    transactions = ServiceTransaction.objects.filter(section='tyre').order_by('-date')
    total = sum(t.amount for t in transactions)
    return render(request, 'services/tyre_list.html', {'transactions': transactions, 'total': total})


@login_required
def tyre_add(request):
    if request.method == 'POST':
        form = TyreTransactionForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.section     = 'tyre'
            t.recorded_by = request.user
            t.save()
            messages.success(request, f'Tyre service recorded. Receipt: {t.receipt_number}')
            return redirect('services:tyre_list')
    else:
        form = TyreTransactionForm()
    return render(request, 'services/tyre_form.html', {'form': form})


@login_required
def battery_list(request):
    transactions = ServiceTransaction.objects.filter(section='battery').order_by('-date')
    total = sum(t.amount for t in transactions)
    return render(request, 'services/battery_list.html', {'transactions': transactions, 'total': total})


@login_required
def battery_add(request):
    if request.method == 'POST':
        form = BatteryTransactionForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.section     = 'battery'
            t.recorded_by = request.user
            t.save()
            messages.success(request, f'Battery service recorded. Receipt: {t.receipt_number}')
            return redirect('services:battery_list')
    else:
        form = BatteryTransactionForm()
    return render(request, 'services/battery_form.html', {'form': form})
