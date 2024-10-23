from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import Products, ProductImage, Variant
from .forms import ProductForm
import base64
import json
from django.core.files.base import ContentFile
from .forms import VariantForm
    


def custom_admin_required(user):
    return user.is_staff  


# def product_detail(request, pk):
#     product = get_object_or_404(Products, pk=pk)
#     variants = product.variants.all()  # Fetch all shape variants for the product
    
#     context = {
#         'product': product,
#         'variants': variants,
#     }
#     return render(request, 'product_detail.html', context)


@user_passes_test(custom_admin_required)

# def add_product(request):
#     if request.method == 'POST':
#         form = ProductForm(request.POST)
#         image_files = request.FILES.getlist('image')  
#         if form.is_valid():
#             product = form.save() 

#             # Save each image associated with the product
#             for image_file in image_files:
#                 image = ProductImage(products=product, image=image_file) 
#                 image.save()  
#             return redirect('products:product_list')
#     else:
#         form = ProductForm()
#     return render(request, 'products/add_product.html', {
#         'form': form,
#     })


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            
            # Get cropped images data
            cropped_images_json = request.POST.get('croppedImages')
            if cropped_images_json:
                cropped_images = json.loads(cropped_images_json)
                
                for idx, img_data in enumerate(cropped_images):
                    if img_data:  # Check if image data exists
                        # Remove data URL header
                        format, imgstr = img_data.split(';base64,')
                        ext = format.split('/')[-1]
                        
                        # Convert base64 to file
                        data = ContentFile(base64.b64decode(imgstr))
                        
                        # Create unique filename
                        file_name = f'product_{product.id}_image_{idx}.{ext}'
                        
                        # Create and save ProductImage instance
                        image = ProductImage(products=product)
                        image.image.save(file_name, data, save=True)

        
            
            variants_data = request.POST.getlist('variants')
            for variant in variants_data:
                carat = variant['carat']
                price = variant['price']
                stock = variant['stock']
                
                Variant.objects.create(product=product, carat=carat, price=price, stock=stock)
            
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


def add_variant(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    
    if request.method == 'POST':
        form = VariantForm(request.POST)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product
            variant.save()
            return redirect('products:product_detail', product_id=product.id)
    else:
        form = VariantForm()
    
    return render(request, 'products/add_variant.html', {
        'form': form,
        'product': product
    })



def product_detail(request, pk):
    product = get_object_or_404(Products, id=pk)
    
    # Get all variants for this product
    variants = Variant.objects.filter(product=product)
    
    return render(request, 'products/product-detail.html', {
        'product': product,
        'variants': variants,
    })