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
from ecomProject import settings
from django.utils.crypto import get_random_string



class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'  
    success_url = reverse_lazy('password_reset_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['domain'] = 'localhost:8000'  
        context['protocol'] = 'http'  
        return context

backend = 'custom_admin.auth_backends.EmailBackend'



def custom_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request.POST)
        if form.is_valid():
            username= form.cleaned_data.get('email')  
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_blocked:
                    messages.error(request, 'Your account is blocked.')
                else:
                    login(request, user)
                    messages.success(request, f'Welcome, {user.email if user.email else user.username}!')
                    return redirect('home')
            else:
                messages.error(request, 'Invalid username or email and password combination.')
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
            user = form.save(commit=False) 
            user.is_active = False  
            otp = get_random_string(length=6, allowed_chars='1234567890')
            print(otp)

            user.save()
            send_mail(
    'Your OTP Code',  
    f"""
    Dear {user.first_name},

    Welcome to Lustrelux!
    Thank you for choosing us for your diamond jewelry needs. We're delighted to have you as part of our community, where elegance and exclusivity meet exceptional craftsmanship. Our collection features stunning diamond jewelry designed to shine on every occasion.

    To complete your registration and unlock your shopping experience, please verify your email address using the One-Time Password (OTP) below:

    Your OTP: "{otp}"

    Please enter this OTP on our website to verify your account and gain access to our exclusive diamond jewelry collections.

    If you have any questions or need assistance, feel free to contact our customer support at support@yourbrand.com. We're here to help you with any queries.

    Thank you for joining us, and we look forward to serving you with the finest diamond pieces.

    Best regards,
    The Lustrelux Team 
    """, 
    settings.DEFAULT_FROM_EMAIL,  
    [user.email], 
    fail_silently=False, 
)
            request.session['user_id'] = user.id  
            request.session['otp'] = otp 
            return redirect('verify_otp')  
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def verify_otp(request):
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        user_id = request.session.get('user_id')
        otp = request.session.get('otp')
        user_id = get_object_or_404(CustomUser, id=user_id)
        
        try:
            if otp == otp_code:
                user_id.is_active = True
                user_id.save()
                del request.session['otp']
                messages.success(request, "OTP verified! Registration complete.")
                return redirect('accounts_login')
            else:
                messages.error(request, "Invalid OTP code. Please try again.")
                return redirect('verify_otp')
        except:
            pass

    return render(request, 'accounts/verify_otp.html')

def resend_otp(request):
    user_id = request.session.get('user_id')
    user = get_object_or_404(CustomUser, id=user_id)
    otp = get_random_string(length=6, allowed_chars='1234567890')
    print(otp)
    send_mail(
    'Your OTP Code',  # The subject (add a comma here)
    f"""
    Dear {user.first_name},

    Welcome to Lustrelux!
    Thank you for choosing us for your diamond jewelry needs. We're delighted to have you as part of our community, where elegance and exclusivity meet exceptional craftsmanship. Our collection features stunning diamond jewelry designed to shine on every occasion.

    To complete your registration and unlock your shopping experience, please verify your email address using the One-Time Password (OTP) below:

    Your OTP: "{otp}"

    Please enter this OTP on our website to verify your account and gain access to our exclusive diamond jewelry collections.

    If you have any questions or need assistance, feel free to contact our customer support at support@yourbrand.com. We're here to help you with any queries.

    Thank you for joining us, and we look forward to serving you with the finest diamond pieces.

    Best regards,
    The Lustrelux Team 
    """, 
    settings.DEFAULT_FROM_EMAIL,  # From email
    [user.email],  # Recipient list
    fail_silently=False,  # Error handling
)

    
    request.session['otp'] = otp
    messages.success(request, "OTP has been resent to your email.")

    return redirect('verify_otp')



@login_required
def home(request):
    products = Products.objects.all()
    categories = Category.objects.all()
    products = Products.objects.prefetch_related('images').all()
    return render(request, 'accounts/home.html', {'products': products, 'categories': categories})
    profile = Profile.objects.get(user=request.user)
    return render(request, 'home.html', {'profile': profile})



def about(request):
    return render(request, 'accounts/about.html') 
def contact(request):
    return render(request, 'accounts/contact.html')

