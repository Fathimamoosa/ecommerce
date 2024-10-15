from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.views import View
from django.core.mail import send_mail
from .forms import CustomUserCreationForm, CustomAuthenticationForm, OTPVerificationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser
from django.db import IntegrityError
from django.contrib import messages
from products.models import Products, Category
from django.contrib.auth import get_backends
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from .models import Profile

# def send_otp_email(user):
#     otp_instance = OTP.objects.create(user=user)
#     send_mail(
#         'Your OTP Code',
#         f'Your OTP code is {otp_instance.otp_code}. This code is valid for 5 minutes.',
#         'from@example.com',
#         [user.email],
#         fail_silently=False,
#     )


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'  # Your custom template
    success_url = reverse_lazy('password_reset_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['domain'] = 'localhost:8000'  # Set your domain for local development
        context['protocol'] = 'http'  # Set protocol for local development
        return context

backend = 'custom_admin.auth_backends.EmailBackend'


def custom_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            # Authenticate the user
            user = authenticate(request, email=email, password=password)

            if user is not None:
                if user.is_blocked:
                    messages.error(request, 'Your account is blocked.')
                else:

                    login(request, user)
                    messages.success(request, f'Welcome, {user.email}!')
                    return redirect('home')  
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Form validation failed.')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})

class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('accounts_login')



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='custom_admin.auth_backends.EmailBackend')
            messages.success(request, "Registration successful! You are now logged in.")
            return redirect('home')  
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

# def register(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)  # Do not save to the database yet
#             user.is_active = False  # Mark user inactive until OTP is verified
#             user.save()
#             send_otp_email(user)  # Send OTP to user's email
#             request.session['user_id'] = user.id  # Store the user ID in session for later use
#             return redirect('verify_otp')  # Redirect to OTP verification page
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = CustomUserCreationForm()

#     return render(request, 'accounts/register.html', {'form': form})


# def verify_otp(request):
#     if request.method == 'POST':
#         otp_code = request.POST.get('otp_code')
#         user_id = request.session.get('user_id')
#         user = get_object_or_404(CustomUser, id=user_id)
        
#         try:
#             otp_instance = OTP.objects.get(user=user, otp_code=otp_code, is_verified=False)
#             if otp_instance.is_expired():
#                 messages.error(request, "OTP expired. Please request a new one.")
#                 return redirect('verify_otp')

#             # OTP is valid
#             otp_instance.is_verified = True
#             otp_instance.save()

#             # Activate the user after OTP verification
#             user.is_active = True
#             user.save()

#             messages.success(request, "OTP verified! Registration complete.")
#             login(request, user, backend='custom_admin.auth_backends.EmailBackend')
#             return redirect('home')
#         except OTP.DoesNotExist:
#             messages.error(request, "Invalid OTP code. Please try again.")

#     return render(request, 'accounts/verify_otp.html')

# def resend_otp(request):
#     user_id = request.session.get('user_id')
#     user = get_object_or_404(CustomUser, id=user_id)
#     otp_resend_count = request.session.get('otp_resend_count', 0)

#     if otp_resend_count < 3:
#         send_otp_email(user)
#         request.session['otp_resend_count'] = otp_resend_count + 1
#         messages.success(request, "OTP has been resent to your email.")
#     else:
#         messages.error(request, "You have reached the maximum OTP resend attempts.")

#     return redirect('verify_otp')



@login_required
def home(request):
    products = Products.objects.all()
    categories = Category.objects.all()
    return render(request, 'accounts/home.html', {'products': products, 'categories': categories})
    profile = Profile.objects.get(user=request.user)
    return render(request, 'home.html', {'profile': profile})
