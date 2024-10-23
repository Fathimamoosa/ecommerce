from django.shortcuts import render,redirect,  get_object_or_404
from .models import Brand
from products.models import Products
from .forms import BrandForm
from django.contrib.auth.decorators import user_passes_test
# def brand_list(request):
#     brands = Brand.objects.all()
#     return render(request, 'brand_list.html', {'brands': brands})

# def brand_detail(request, brand_id):
#     brand = get_object_or_404(Brand, id=brand_id)
#     products = Product.objects.filter(brand=brand)
#     return render(request, 'brand_detail.html', {'brand': brand, 'products': products})


def admin_check(user):
    return user.is_authenticated and user.is_superuser 

@user_passes_test(admin_check, login_url = 'admin_login')
def Brand_list(request):
    brands = Brand.all_objects.all()
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save
            return redirect('brand_list')
    else:
        form = BrandForm()
    return render(request, 'brand/brand_list.html', {'brands' : brands, 'form': form})

@user_passes_test(admin_check, login_url='admin_login')
def brand_create(request):
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('brand_list')
    else:
        form = BrandForm()
    return render(request, 'brand/brand_form.html', {'form': form})



@user_passes_test(admin_check, login_url='admin_login')
def brand_update(request, pk):
    brand = get_object_or_404(Brand.all_objects, pk=pk)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            return redirect('brand_list')
    else:
        form = BrandForm(instance=brand)
    return render(request, 'brand/brand_form.html', {'form': form})

@user_passes_test(admin_check, login_url='admin_login')
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        brand.delete()
        return redirect('brand_list')
    return render(request, 'brand/brand_confirm_delete.html', {'brand': brand})

@user_passes_test(admin_check, login_url='admin_login')
def restore_brand(request, pk):
    brand = get_object_or_404(Brand.all_objects, pk=pk)
    if request.method == 'POST':
        brand.is_deleted = False
        brand.save()
        return redirect('brand_list')
    return render(request, 'custom_admin/restore_confirmation.html', {'brand': brand})