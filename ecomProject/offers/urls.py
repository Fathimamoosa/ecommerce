from django.urls import path
from . import views


app_name = 'offers'


urlpatterns = [
    path('offers/', views.manage_offers, name='offers'),  # Add the 'name' argument
]