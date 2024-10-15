# products/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import Products, ProductImage
from .forms import ProductForm

# Check if user is a customAdmin (or use your custom admin check)
def custom_admin_required(user):
    return user.is_staff  # Or your custom admin condition

# @user_passes_test(custom_admin_required)
# def add_product(request):
#     if request.method == 'POST':
#         form = ProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('products:product_list')
#     else:
#         form = ProductForm()
#     return render(request, 'products/add_product.html', {'form': form})


@user_passes_test(custom_admin_required)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        # Get the list of images
        image_files = request.FILES.getlist('image')  
        if form.is_valid():
            product = form.save() 

            # Save each image associated with the product
            for image_file in image_files:
                image = ProductImage(product=product, image=image_file)
                image.save()  # Save the image
            return redirect('products:product_list')
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {
        'form': form,
    })


# @user_passes_test(custom_admin_required)
# def edit_product(request, pk):
#     product = get_object_or_404(Products.all_objects, pk=pk)
#     if request.method == 'POST':
#         form = ProductForm(request.POST, instance=product)
#         if form.is_valid():
#             form.save()
#             return redirect('products:product_list')
#     else:
#         form = ProductForm(instance=product)
#     return render(request, 'products/edit_product.html', {'form': form})

@user_passes_test(custom_admin_required)
def edit_product(request, pk):
    product = get_object_or_404(Products.all_objects, pk=pk)
    existing_images = product.images.all() 
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        
        if form.is_valid():
            product = form.save() 
            
            # Handle the uploaded images
            image_files = request.FILES.getlist('image')  
            
            # Save each new image associated with the product
            for image_file in image_files:
                ProductImage.objects.create(product=product, image=image_file)

            return redirect('products:product_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/edit_product.html', {
        'form': form,
        'existing_images': existing_images,
    })



@user_passes_test(custom_admin_required)
def soft_delete_product(request, pk):
    product = get_object_or_404(Products, pk=pk)
    product.is_deleted = True
    product.save()
    return redirect('products:product_list')

@user_passes_test(custom_admin_required)
def product_list(request):
    products = Products.all_objects.all()
    product_images = {product.id: product.images.first() for product in products}
    return render(request, 'products/product_list.html', {'products': products, 'product_images': product_images})


@user_passes_test(custom_admin_required)
def restore_product(request, pk):
    product = get_object_or_404(Products.all_objects, pk=pk)
    if request.method == 'POST':
        product.is_deleted = False
        product.save()
        return redirect('products:product_list')  
    return render(request, 'custom_admin/restore_confirmation.html', {'product': product})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Products, pk = pk)
    images = product.images.all()
    return render(request, 'products/product-detail.html', {'product':product, 'images': images})