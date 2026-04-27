from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('accounts/', include('accounts.urls')),
    path('parking/', include('parking.urls')),
    path('services/', include('services.urls')),
    path('reports/', include('reports.urls')),
]
