from django.urls import path
from . import views


app_name = 'orders'

urlpatterns = [
    path('orders/', views.order_list, name='order_list'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('place_order/', views.place_order, name='place_order'),
    path('orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('orders/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path("redirect-to-payment/", views.redirect_to_payment, name="redirect_to_payment"),
    path("order/success/<int:order_id>/", views.order_success, name="order_success"),
    path('return/<int:order_id>/', views.return_order, name='return_order'),
    path('success/<str:order_number>/<str:total_price_after_discount>/', views.order_success, name='order_success'),
    path('retry-payment/<int:order_id>/', views.retry_payment, name='retry_payment'),
    path('generate-invoice/<int:order_id>/download/', views.generate_invoice, name='generate_invoice'),
    path('payment-success/', views.payment_success, name='payment_success'),
]

    