from django.urls import path
from .views import apply_selected_coupon, remove_coupon,  available_coupons




urlpatterns = [
    path('remove-coupon/', remove_coupon, name='remove_coupon'),
    path('apply-coupon/<str:coupon_code>/', apply_selected_coupon, name='apply_selected_coupon'),
    path('available-coupons/', available_coupons, name='available_coupons'),
]