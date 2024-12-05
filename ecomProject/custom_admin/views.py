from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .forms import CustomUserForm, CustomLoginForm 
from accounts.models import *
from category.models import Category
from django.utils import timezone
from .forms import CategoryForm


def admin_check(user):
    return user.is_authenticated and user.is_staff and user.is_superuser

class LoginView(View):
    def get(self, request):
        form = CustomLoginForm()
        print('90')
        return render(request, 'custom_admin/login.html', {'form': form})

    def post(self, request):
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')  # Maps to email
            password = form.cleaned_data.get('password')
            print(f"Attempting to authenticate: {username} with password {password}")
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
                print(f"Authenticated user: {user.email}")
            else:
                print("Authentication failed.")
        return render(request, 'custom_admin/login.html', {'form': form})


def dashboard(request):
    return render(request, 'custom_admin/dashboard.html')

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('admin_login')  

@method_decorator(user_passes_test(admin_check, login_url='admin_login'), name='dispatch')
class UserListView(View):
    def get(self, request):
        users = CustomUser.objects.all()
        return render(request, 'custom_admin/user_list.html', {'users': users})

    def post(self, request):
        action = request.POST.get('action')
        user_ids = request.POST.getlist('user_ids')

        if action == 'block':
            CustomUser.objects.filter(id__in=user_ids).update(is_blocked=True)
            messages.success(request, "Selected users have been blocked.")
        elif action == 'unblock':
            CustomUser.objects.filter(id__in=user_ids).update(is_blocked=False)
            messages.success(request, "Selected users have been unblocked.")
        else:
            messages.error(request, "Invalid action.")

        return redirect('user_list')

@method_decorator(user_passes_test(admin_check, login_url='admin_login'), name='dispatch')
class UserCreateView(View):
    def get(self, request):
        form = CustomUserForm()
        return render(request, 'custom_admin/user_form.html', {'form': form})

    def post(self, request):
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
        return render(request, 'custom_admin/user_form.html', {'form': form})

@method_decorator(user_passes_test(admin_check, login_url='admin_login'), name='dispatch')
class UserUpdateView(View):
    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        form = CustomUserForm(instance=user)
        return render(request, 'custom_admin/user_form.html', {'form': form})

    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
        return render(request, 'custom_admin/user_form.html', {'form': form})


@method_decorator(user_passes_test(admin_check, login_url='admin_login'), name='dispatch')
class UserDeleteView(View):
    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        return render(request, 'custom_admin/user_confirm_delete.html', {'user': user})

    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.delete()
        return redirect('user_list')

@user_passes_test(admin_check, login_url='admin_login')
def category_list(request):
    categories = Category.all_objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'category/category_list.html', {'categories': categories, 'form': form})


@user_passes_test(admin_check, login_url='admin_login')
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'category/form.html', {'form': form})


@user_passes_test(admin_check, login_url='admin_login')
def category_update(request, pk):
    category = get_object_or_404(Category.all_objects, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category/category_form.html', {'form': form})

@user_passes_test(admin_check, login_url='admin_login')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.is_deleted = False
        category.save()
        category.delete()
        return redirect('category_list')
    return render(request, 'category/category_confirm_delete.html', {'category': category})


@user_passes_test(admin_check, login_url='admin_login')
def restore_category(request, pk):
    category = get_object_or_404(Category.all_objects, pk=pk)
    if request.method == 'POST':
        category.is_deleted = False
        category.save()
        return redirect('category_list')  
    return render(request, 'custom_admin/restore_confirmation.html', {'category': category})
