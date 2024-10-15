from django.db import models
from category.models import Category
from category.managers import CategoryManager, AllCategoryManager
from PIL import Image
import os

    # images = models.ImageField(upload_to='photos/products')
    # image_2  = models.ImageField(upload_to='photos/products')
    # image_3 = models.ImageField(upload_to='photos/products')

# Create your models here.
class Products(models.Model):
    product_name = models.CharField(max_length = 200, unique = True)
    slug = models.SlugField(max_length = 200, unique = True)
    description = models.TextField(max_length = 500, blank = True)
    price = models.IntegerField()
    stock = models.IntegerField()
    is_available = models.BooleanField(default = True)
    category = models.ForeignKey(Category, on_delete = models.CASCADE)
    created_date = models.DateTimeField(auto_now = True)
    modified_date = models.DateTimeField(auto_now = True)
    is_deleted = models.BooleanField(default=False) 

    objects = CategoryManager()  # For regular users
    all_objects = AllCategoryManager()  # For admin

class ProductImage(models.Model):
    product = models.ForeignKey(Products, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/images/')

    def __str__(self):
        return f"Image for {self.product.name}"




    def save(self, *args, **kwargs):
        # First save the image (without cropping)
        super().save(*args, **kwargs)

        # Define the cropping logic
        if self.images:
            img_path = self.images.path
            img_path_2 = self.image_2.path
            img_path_3 = self.image_3.path
            img = Image.open(img_path)
            img_2 = Image.open(img_path_2)
            img_3 = Image.open(img_path_3)
            # Resize the image to 300x300, maintaining the aspect ratio
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            img_2.thumbnail((300, 300), Image.Resampling.LANCZOS)
            img_3.thumbnail((300,300), Image.Resampling.LANCZOS)   
            # Save the resized image, overwriting the original
            img.save(img_path)
            img_2.save(img_path_2)
            img_3.save(img_path_3)


    def __str__(self):
        return self.product_name
    
