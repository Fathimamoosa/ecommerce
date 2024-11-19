from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.views import View
from django.core.mail import send_mail
from .forms import CustomUserCreationForm, CustomAuthenticationForm, OTPVerificationForm, EditUserForm, AddAddressForm, CustomUserUpdateForm, ProfileForm, AddressForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, Address, Profile
from django.db import IntegrityError
from django.contrib import messages
from products.models import Products, Category, Variant
from django.contrib.auth import get_backends
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from ecomProject import settings
from django.utils.crypto import get_random_string
from django.views.generic import UpdateView, DetailView, ListView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib.auth import logout
from orders.models import Order, OrderItem

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
            email= form.cleaned_data.get('email')  
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=email, password=password)

            if user is not None:
                if user.is_superuser or user.is_staff:
                    messages.error(request, 'Admin accounts cannot log in from the user side.')
                elif user.is_blocked:
                    messages.error(request, 'Your account is blocked.')
                else:
                    login(request, user)  # Log the user in
                    messages.success(request, f'Welcome, {user.email if user.email else user.username}!')
                    return redirect('home')  # Redirect to the desired page after login
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


def home(request):
    products = Products.objects.filter(category__is_deleted=False).prefetch_related('images')
    categories = Category.objects.filter(is_deleted=False)
    variants = Variant.objects.filter(product__category__is_deleted=False)

    return render(request, 'accounts/home.html', {
        'products': products,
        'categories': categories,
        'variants': variants
    })

    # products = Products.objects.all()
    # categories = Category.objects.all()
    # variants = Variant.objects.all() 
    # products = Products.objects.prefetch_related('images').all()
    # return render(request, 'accounts/home.html', {'products': products, 'categories': categories, 'variants' : variants})
    profile = Profile.objects.get(user=request.user)
    return render(request, 'home.html', {'profile': profile})

def about(request):
    return render(request, 'accounts/about.html') 

def contact(request):
    return render(request, 'accounts/contact.html')



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False 
            
            otp = get_random_string(length=6, allowed_chars='1234567890')
            send_otp_email(user, otp)
            print(otp) 
            
            user.save() 
            request.session['user_id'] = user.id
            request.session['otp'] = otp
            messages.success(request, "Registration successful! Please check your email for the OTP.")
            return redirect('verify_otp')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

def send_otp_email(user, otp):
    send_mail(
        'Your OTP Code',
        f"""
        Dear {user.first_name},

        Welcome to Lustrelux! To complete your registration, please verify your email with the OTP below:

        Your OTP: "{otp}"

        Please enter this OTP on our website to verify your account.

        Best regards,
        The Lustrelux Team
        """,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

def verify_otp(request):
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        user_id = request.session.get('user_id')
        otp = request.session.get('otp')
        user = get_object_or_404(CustomUser, id=user_id)

        if otp and otp == otp_code:  
            user.is_active = True
            user.save()
            del request.session['otp']  
            messages.success(request, "OTP verified! Registration complete.")
            return redirect('accounts_login')
        else:
            messages.error(request, "Invalid OTP code. Please try again.")

    return render(request, 'accounts/verify_otp.html')

def resend_otp(request):
    user_id = request.session.get('user_id')
    user = get_object_or_404(CustomUser, id=user_id)
    
    otp = get_random_string(length=6, allowed_chars='1234567890')
    send_otp_email(user, otp)  
    print(otp)
    
    request.session['otp'] = otp 
    messages.success(request, "OTP has been resent to your email.")
    return redirect('verify_otp')

class UserProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'accounts/profile.html'
    context_object_name = 'user'

    def get_object(self):
        return self.request.user




class UserAddressesView(LoginRequiredMixin, ListView):
    model = Address
    template_name = 'accounts/user_addresses.html'
    context_object_name = 'addresses'

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

class AddAddressView(LoginRequiredMixin, CreateView):
    form_class =AddressForm
    template_name = 'accounts/add_address.html'
    success_url = reverse_lazy('user_addresses')

    def form_valid(self, form):
        address = form.save(commit=False)
        address.user = self.request.user
        address.save()
        messages.success(self.request, "Address added successfully!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['addresses'] = Address.objects.filter(user=self.request.user).order_by('-is_default')
        return context
    
class EditAddressView(LoginRequiredMixin, UpdateView):
    model = Address
    form_class = AddressForm
    template_name = 'accounts/edit_address.html'
    success_url = reverse_lazy('user_addresses')

    def form_valid(self, form):
        messages.success(self.request, "User Address Updated Successfully")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['addresses'] = Address.objects.filter(user=self.request.user).order_by('-is_default')
        return context

class DeleteAddressView(LoginRequiredMixin, DeleteView):
    model = Address
    template_name = 'accounts/confirm_delete_address.html'
    success_url = reverse_lazy('user_addresses')
    context_object_name = 'address'

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Address deleted successfully.")
        return super().delete(request, *args, **kwargs)



def edit_profile(request):
    user = request.user  
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)  
        if form.is_valid():
            form.save()
    else:
        form = ProfileForm(instance=user)  

    return render(request, 'accounts/edit_profile.html', {'form': form})



@login_required
def set_default_address(request, address_id):

    address = get_object_or_404(Address, id=address_id, user=request.user)
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)

  
    address.is_default = True
    address.save()

    if request.is_ajax():
        return JsonResponse({'success': True, 'address_id': address.id})
    return JsonResponse({'success': False}, status=400)

def user_order_items(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).order_by('-order_date')

        return render(request, 'accounts/orders.html', {'orders': orders})
    else:
        return redirect('login')