from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('prices/',           views.price_list, name='price_list'),
    path('prices/set/',       views.set_price,  name='set_price'),
    path('prices/<int:pk>/',  views.set_price,  name='edit_price'),
    path('tyre/',             views.tyre_list,  name='tyre_list'),
    path('tyre/add/',         views.tyre_add,   name='tyre_add'),
    path('battery/',          views.battery_list, name='battery_list'),
    path('battery/add/',      views.battery_add,  name='battery_add'),
]
