from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('', views.my_wallet_view, name='my_wallet'),
    path('wallet_history/', views.wallet_history_view, name='wallet_history'),
]