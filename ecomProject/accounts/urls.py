from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import *
from products.views import product_detail
from .views import CustomPasswordResetView, edit_profile,  UserAddressesView, AddAddressView, EditAddressView, DeleteAddressView, set_default_address
from . import views
from products.views import ProductListView
from coupons.views import admin_coupon_list, admin_coupon_add, admin_coupon_edit 


urlpatterns = [
    path('register/',register,name = 'accounts_register'),
    path('login/', custom_login, name='accounts_login'),
    path('logout/', LogoutView.as_view(), name='accounts_logout'),
    path('', home, name = 'home'),
    path('product_detail/<int:pk>/',product_detail, name = 'product_detail'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('resend-otp/', resend_otp, name='resend_otp'),
    path('change_password/', auth_views.PasswordChangeView.as_view(template_name='accounts/change_password.html'), name='change_password'),
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
    path('change_password/', auth_views.PasswordChangeView.as_view(template_name='change_password.html',success_url='/'), name='change_password'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('product/', ProductListView.as_view(template_name='products/product.html'), name='product_list'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('order-items/', views.user_order_items, name='orders'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('user_addresses/', views.UserAddressesView.as_view(), name='user_addresses'),
    path('add_address/', views.AddAddressView.as_view(), name='add_address'),
    path('edit_address/<int:pk>/', views.EditAddressView.as_view(), name='edit_address'),
    path('delete_address/<int:pk>/', views.DeleteAddressView.as_view(), name='delete_address'),
    path('set-default-address/<int:address_id>/', views.set_default_address, name='set_default_address'),
    path('coupons/', admin_coupon_list, name='admin_coupon_list'),
    path('coupons/add/', admin_coupon_add, name='admin_coupon_add'),
    path('coupons/edit/<int:pk>/', admin_coupon_edit, name='admin_coupon_edit'),
]

 



