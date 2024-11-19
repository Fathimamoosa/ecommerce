from django.db import models
from category.models import Category
from category.managers import CategoryManager, AllCategoryManager
from PIL import Image
import os
from brand.models import Brand
from django.urls import reverse
from accounts.models import CustomUser

 

class Products(models.Model):
    product_name = models.CharField(max_length = 200, unique = True)
    description = models.TextField(max_length = 500, blank = True)
    # stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default = True)
    category = models.ForeignKey(Category, on_delete = models.CASCADE)
    created_date = models.DateTimeField(auto_now = True)
    modified_date = models.DateTimeField(auto_now = True)
    is_deleted = models.BooleanField(default=False) 
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    objects = CategoryManager()  
    all_objects = AllCategoryManager()  

    def __str__(self):
        return self.product_name

class ProductImage(models.Model):
    products = models.ForeignKey(Products, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/images/')


    def __str__(self):
        return f"Image for {self.products.product_name}"



class Variant(models.Model):
    product = models.ForeignKey(Products, related_name='variants', on_delete=models.CASCADE)
    carat = models.DecimalField(max_digits=5, decimal_places=2, default=None)  
    price = models.DecimalField(max_digits=10, decimal_places=2, default = None)  
    stock = models.PositiveIntegerField(default=0)

    def in_stock(self):
        return self.stock >0

    def __str__(self):
        return f"{self.price} - {self.carat} carat {self.stock} stock"
    
    def get_url(self):
        """Get the URL of the product detail page for this variant."""
        return reverse('products:product_detail', args=[self.product.id])

class Review(models.Model):
    product = models.ForeignKey(Products, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.product_name} by {self.user.username}"