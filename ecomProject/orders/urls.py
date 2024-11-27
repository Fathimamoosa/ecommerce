from django.urls import path
from . import views


app_name = 'orders'

urlpatterns = [
    path('orders/', views.order_list, name='order_list'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('success/<str:order_number>/<str:total_price>/', views.order_success, name='order_success'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('orders/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    # path('payment/initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('paymnet/payment/callback/', views.payment_callback, name='payment_callback'),
    path('proceed-to-pay', views.razorpaycheck)

]

    