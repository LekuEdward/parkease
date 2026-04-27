from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, UserCreateForm
from .models import CustomUser


def login_view(request):
    """Login page with split-panel ParkEase design."""
    if request.user.is_authenticated:
        return redirect('parking:dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('parking:dashboard')
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def user_list(request):
    if not request.user.is_admin():
        messages.error(request, "Access denied. Admin only.")
        return redirect('parking:dashboard')
    users = CustomUser.objects.all().order_by('role', 'username')
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
def create_user(request):
    if not request.user.is_admin():
        messages.error(request, "Access denied. Admin only.")
        return redirect('parking:dashboard')
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully!')
            return redirect('accounts:user_list')
    else:
        form = UserCreateForm()
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Create New User'})
