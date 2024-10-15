from django.db import models
from django.utils import timezone
from category.managers import CategoryManager, AllCategoryManager
from PIL import Image
import os
# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length = 50, unique = True)
    slug = models.CharField(max_length = 100, unique = True)
    description = models.TextField(max_length = 255, blank = True)
    cat_image = models.ImageField(upload_to='photos/categories')
    is_deleted = models.BooleanField(default=False)  # Soft delete flag
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = CategoryManager()  # For regular users
    all_objects = AllCategoryManager()  # For admin

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()


    def save(self, *args, **kwargs):
        # First save the image (without cropping)
        super().save(*args, **kwargs)

        # Define the cropping logic
        if self.cat_image:
            img_path = self.cat_image.path
            img = Image.open(img_path)

            # Resize the image to 300x300, maintaining the aspect ratio
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)

            # Save the resized image, overwriting the original
            img.save(img_path)


    def __str__(self):
        return self.category_name
    