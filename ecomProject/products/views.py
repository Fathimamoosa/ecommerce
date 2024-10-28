from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import Products, ProductImage, Variant, Category
from .forms import ProductForm
import base64
import json
from django.core.files.base import ContentFile
from .forms import VariantForm
from django.views import View
from django.db import models
from django.views.generic import ListView




    


def custom_admin_required(user):
    return user.is_staff  

@user_passes_test(custom_admin_required)


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            cropped_images_json = request.POST.get('croppedImages')
            if cropped_images_json:
                cropped_images = json.loads(cropped_images_json)
                
                for idx, img_data in enumerate(cropped_images):
                    if img_data: 
                        format, imgstr = img_data.split(';base64,')
                        ext = format.split('/')[-1]
                        
                        data = ContentFile(base64.b64decode(imgstr))
                        file_name = f'product_{product.id}_image_{idx}.{ext}'
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


@user_passes_test(custom_admin_required)
def edit_product(request, pk):
    product = get_object_or_404(Products.all_objects, pk=pk)
    existing_images = product.images.all() 
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        
        if form.is_valid():
            product = form.save() 
            image_files = request.FILES.getlist('image')  
            
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
    variants = Variant.objects.filter(product=product)
    images = ProductImage.objects.filter(products=product)
    related_products = Products.objects.filter(category=product.category).exclude(id=product.id)[:5]  
    return render(request, 'products/product-detail.html', {
        'product': product,
        'variants': variants,
        'images': images,
        'related_products': related_products,  
    })





class DeleteImageView(View):
    def get(self, request, image_id):
        image = get_object_or_404(ProductImage, id=image_id)
        product_id = image.product.id 
        product = image.product # Assuming `ProductImage` has a foreign key to `Product`
        image.delete()
        return redirect('edit_product', product_id=product_id)

class ProductImageView(View):
    def get(self, request, product_id):
        product = get_object_or_404(Products, id=product_id)
        images = product.images.all()  # Get related images
        return render(request, 'product_images.html', {'product': product, 'images': images})
    
@login_required
def product_view(request, product_id):
    product = Products.objects.get(id=product_id)
    product_images = product.images.all() 
    categories = Category.all_objects.all()
    print('hai')
    return render(request, 'products/product.html', {
        'product': product,
        'product_images': product_images,
        'categories': categories
    })
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        # Get selected categories from GET parameters
        selected_categories = [int(id) for id in self.request.GET.getlist('category') if id.isdigit()]
        context['selected_categories'] = selected_categories
        return context

    def get_queryset(self):
        queryset = Product.objects.all()
        categories = self.request.GET.getlist('category')
        if categories:
            queryset = queryset.filter(category_id__in=categories)
        return queryset

    def get_absolute_url(self):
        return f"/category/{self.id}/" 
class ProductListView1(ListView):
    model = Products
    template_name = 'product.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        # Get selected categories from GET parameters
        selected_categories = [int(id) for id in self.request.GET.getlist('category') if id.isdigit()]
        context['selected_categories'] = selected_categories
        print(context)
        return context

    def get_queryset(self):
        queryset = Products.objects.all()
        categories = self.request.GET.getlist('category')
        if categories:
            queryset = queryset.filter(category_id__in=categories)
        return queryset
    
class ProductListView(ListView):
    model = Variant
    template_name = 'product.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        # Get selected categories from GET parameters
        selected_categories = [int(id) for id in self.request.GET.getlist('category') if id.isdigit()]
        context['selected_categories'] = selected_categories
        print(context)
        return context

    def get_queryset(self):
        queryset = Variant.objects.all()
        categories = self.request.GET.getlist('category')
        if categories:
            queryset = queryset.filter(category_id__in=categories)
        return queryset