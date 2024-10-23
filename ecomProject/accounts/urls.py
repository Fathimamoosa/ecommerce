from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import *
from products.views import product_detail
from .views import CustomPasswordResetView  



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
    #path('verify-otp/', verify_otp, name='verify_otp'),
    #path('resend-otp/', resend_otp, name='resend_otp'),
    
    # URL for password change view
    path('change_password/', auth_views.PasswordChangeView.as_view(template_name='accounts/change_password.html'), name='change_password'),

    # URL for password change success page
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
    path('change_password/', auth_views.PasswordChangeView.as_view(
        template_name='change_password.html',
        success_url='/'
    ), name='change_password'),
]


