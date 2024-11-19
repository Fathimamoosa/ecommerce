from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import Products, ProductImage, Variant, Category, Brand, Review
from .forms import ProductForm
import base64
import json
from django.core.files.base import ContentFile
from .forms import VariantForm
from django.views import View
from django.db import models
from django.views.generic import ListView
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from cart.views import _cart_id
from cart.models import CartItem
from django.db.models import Min, Max
from .forms import ReviewForm

def custom_admin_required(user):
    return user.is_staff  

@user_passes_test(custom_admin_required)


def add_product(request):
    if request.method == 'POST':
        print(request.POST)
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

        
            
            # variants_data = request.POST.getlist('variants')
            variants_data = json.loads(request.POST.get('variantsData'))
            
            print(variants_data)
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
    existing_variants = Variant.objects.all()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        
        if form.is_valid():
            product = form.save() 
            image_files = request.FILES.getlist('image')  
            
            for image_file in image_files:
                ProductImage.objects.create(products=product, image=image_file)

            variants_data = request.POST.get('variantsData')
            if variants_data:
                variants = json.loads(variants_data)
                existing_variant_ids = [variant.id for variant in existing_variants]

                for variant_data in variants:
                    variant_id = variant_data.get('id')
                    carat = variant_data['carat']
                    price = variant_data['price']
                    stock = variant_data['stock']

                    if variant_id:  # Update existing variant
                        variant = Variant.objects.get(id=variant_id)
                        variant.carat = carat
                        variant.price = price
                        variant.stock = stock
                        variant.save()
                        existing_variant_ids.remove(variant.id)
                    else:  # Add new variant
                        Variant.objects.create(product=product, carat=carat, price=price, stock=stock)

                # Delete variants not in the submitted data
                Variant.objects.filter(id__in=existing_variant_ids).delete()

            return redirect('products:product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/edit_product.html', {
        'form': form,
        'existing_images': existing_images,
        'existing_variants': existing_variants,
    })



@user_passes_test(custom_admin_required)
def soft_delete_product(request, pk):
    product = get_object_or_404(Products, pk=pk)
    product.is_deleted = True
    product.save()
    messages.success(request, f'The product "{product.product_name}" has been soft deleted successfully.')
    return redirect('products:product_list')

@user_passes_test(custom_admin_required)
def product_list(request):
    products = Products.all_objects.all()
    product_images = {product.id: product.images.first() for product in products}
    paginator = Paginator(products, 4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    context = {
        'products': products,
        'product_images': product_images,
        'page_obj' : page_obj
    }
    return render(request, 'products/product_list.html', context)


@user_passes_test(custom_admin_required)
def restore_product(request, pk):
    product = get_object_or_404(Products.all_objects, pk=pk)
    if request.method == 'POST':
        product.is_deleted = False
        product.save()
        return redirect('products:product_list')  
    return render(request, 'custom_admin/restore_confirmation.html', {'product': product})


@login_required
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
    variant = get_object_or_404(Variant, id=pk)
    product = variant.product
    variants = Variant.objects.filter(product=product)
    images = ProductImage.objects.filter(products=product)
    in_cart = CartItem.objects.filter(cart__cart_id= _cart_id(request), variant= variant).exists()
    
    related_products = Products.objects.filter(category=product.category).exclude(id=product.id)[:5]

    if variant.stock > 0:
        # Logic to add product to cart or process order
        variant.stock -= 1
        variant.save()
        print(variant.stock)
        

    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            if request.user.is_authenticated:
                review.user = request.user
            review.save()
            messages.success(request, "Thank you for your review!")
            return redirect('product_detail', pk=pk)
        else:
            messages.error(request, "Please correct the errors in the review form.")

    else:
        review_form = ReviewForm()

    # Fetch existing reviews
    reviews = Review.objects.filter(product=product).order_by('-created_date')

    context = {
        'product': product,
        'variant': variant,
        'variants': variants,
        'images': images,
        'related_products': related_products,
        'in_cart': in_cart,
        'reviews': reviews,
        'review_form': review_form,  # Pass the form to the template
    }
    return render(request, 'products/product-detail.html', context)

        # Optional: You could check if a user is logged in and use the user ID
        # if request.user.is_authenticated:
        #     user = request.user
        # else:
        #     user = None  # or use a default name for anonymous users

        # if rating and review_text:
        #     Review.objects.create(
        #         product=product,
        #         user=user,
        #         rating=rating,
        #         review_text=review_text
        #     )

    #     return redirect('product_detail', pk=pk)  # Redirect after form submission to avoid resubmission

    # # Get reviews for the product
    # reviews = Review.objects.filter(product=product).order_by('-created_date')

    # context = {
    #     'product': product,
    #     'variant': variant,
    #     'variants': variants,
    #     'images': images,
    #     'related_products': related_products,
    #     'in_cart': in_cart,
    #     'reviews': reviews,  # Pass the reviews to the template
    # }

    # return render(request, 'products/product-detail.html', context)

class DeleteImageView(View):
    def get(self, request, image_id):
        image = get_object_or_404(ProductImage, id=image_id)
        product_id = image.products.id 
        image.delete()
        return redirect(reverse('products:edit_product', kwargs={'pk': product_id}))
    
        return redirect('edit_product', product_id=product_id)

class ProductImageView(View):
    def get(self, request, product_id):
        product = get_object_or_404(Products, id=product_id)
        images = product.images.all()  
        return render(request, 'product_images.html', {'product': product, 'images': images})
    
@login_required
def product_view(request, product_id):
    product = Products.objects.get(id=product_id)
    categories = Category.all_objects.all()

    # Sorting for product images
    sort_by = request.GET.get('sort')  # Get the sorting parameter
    product_images = product.images.all()

    if sort_by == 'a_to_z':
        product_images = product_images.order_by('id')  # Adjust 'id' to a relevant field
    elif sort_by == 'z_to_a':
        product_images = product_images.order_by('-id')  # Adjust '-id' to a relevant field

    return render(request, 'products/product.html', {
        'product': product,
        'product_images': product_images,
        'categories': categories
    })
# def product_view(request, product_id):
#     product = Products.objects.get(id=product_id)
#     product_images = product.images.all() 
#     categories = Category.all_objects.all()
#     return render(request, 'products/product.html', {
#         'product': product,
#         'product_images': product_images,
#         'categories': categories
#     })
    


class ProductListView1(ListView):
    model = Products
    template_name = 'product.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_categories = [int(id) for id in self.request.GET.getlist('category') if id.isdigit()]
        context['selected_categories'] = selected_categories
        return context

    def get_queryset(self):
        queryset = Products.objects.filter(category__is_deleted=False)  
        categories = self.request.GET.getlist('category')
        if categories:
            queryset = queryset.filter(category_id__in=categories)
        return queryset

class ProductListView(ListView):
    model = Variant
    template_name = 'product.html'
    context_object_name = 'variants'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        context['categories'] = categories
        selected_categories = [int(id) for id in self.request.GET.getlist('category') if id.isdigit()]
        context['selected_categories'] = selected_categories
        context['sort'] = self.request.GET.get('sort', '') 
        # Add price range to the context
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '') 
        context['query'] = self.request.GET.get('q', '') # Add current sort to context
        return context

    def get_queryset(self):

        # queryset = Products.objects.filter(is_deleted=False, is_available=True)
        queryset = Variant.objects.filter(product__category__is_deleted=False)
        categories = self.request.GET.getlist('category')
        sort = self.request.GET.get('sort')
        query = self.request.GET.get('q')

        # Filter by category
        if categories:
            queryset = queryset.filter(product__category_id__in=categories)

        # Sort by the requested order
        sort_by = self.request.GET.get('sort')
        if sort_by == 'a_to_z':
            queryset = queryset.order_by('product__product_name')  # Use correct field
        elif sort_by == 'z_to_a':
            queryset = queryset.order_by('-product__product_name')  # Use correct field
        if query:
            queryset = queryset.filter(
                product__product_name__icontains=query
            ) | queryset.filter(
                product__description__icontains=query
            )

        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if sort == 'price_low_to_high':
            queryset = queryset.order_by('price')
        elif sort == 'price_high_to_low':
            queryset = queryset.order_by('-price')
        # elif sort == 'new_arrival':
        #     queryset = queryset.order_by('-product__created_date')

        return queryset.distinct()

# def search_products_view(request):
#     query = request.GET.get("search-product")
#     print("Search Query:", query) 
#     products = []

#     if query:
#         products = Products.objects.filter(
#             Q(product_name__icontains=query) | Q(description__icontains=query)
#         ).order_by("created_date")
#     context = {
#         "products" : products,
#         "query" : query,
#     }
#     return render(request, 'products/search_products.html', context )


# def product_list(request):
#     products = Products.objects.all()

#     # Filters
#     category_id = request.GET.get('category')
#     if category_id:
#         products = products.filter(category_id=category_id)

#     brand_id = request.GET.get('brand')
#     if brand_id:
#         products = products.filter(brand_id=brand_id)

#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')
#     if min_price and max_price:
#         products = products.filter(price__gte=min_price, price__lte=max_price)
#     elif min_price:
#         products = products.filter(price__gte=min_price)

#     sort_order = request.GET.get('sort')
#     if sort_order == 'az':
#         products = products.order_by('title')
#     elif sort_order == 'za':
#         products = products.order_by('-title')
#     elif sort_order == 'price_low':
#         products = products.order_by('price')
#     elif sort_order == 'price_high':
#         products = products.order_by('-price')

#     categories = Category.objects.all()
#     brands = Brand.objects.all()

#     return render(request, 'product_list.html', {
#         'products': products,
#         'categories': categories,
#         'brands': brands,
#     })