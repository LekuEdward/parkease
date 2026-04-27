from django.urls import path
from . import views

app_name = 'parking'

urlpatterns = [
    path('',                              views.dashboard,       name='dashboard'),
    path('vehicles/',                     views.vehicle_list,    name='vehicle_list'),
    path('register/',                     views.register_vehicle,name='register'),
    path('<int:pk>/edit/',                views.edit_vehicle,    name='edit_vehicle'),
    path('<int:pk>/delete/',              views.delete_vehicle,  name='delete_vehicle'),
    path('signout/',                      views.signout_search,  name='signout_search'),
    path('signout/<int:pk>/',             views.signout_process, name='signout_process'),
    path('receipt/<str:receipt_number>/', views.receipt_view,    name='receipt'),
    path('history/',                      views.history,         name='history'),
]
