from django.urls import path
from . import views

app_name = "payments"

urlpatterns =[
    path('payment_success', views.payment_success, name='payment_success'),
    path("payment/", views.payment, name="payment"),
    path('payment_callback/', views.payment_callback, name='payment_callback'),
]