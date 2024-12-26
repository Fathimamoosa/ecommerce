from django.db import models
from django.utils import timezone
from category.managers import CategoryManager, AllCategoryManager
from PIL import Image
from offers.models import CategoryOffer
import os
 
class Category(models.Model):
    category_name = models.CharField(max_length = 50, unique = True)
    description = models.TextField(max_length = 255, blank = True)
    cat_image = models.ImageField(upload_to='photos/categories')
    is_deleted = models.BooleanField(default=False)  
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = CategoryManager()  
    all_objects = AllCategoryManager()

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.cat_image:
            img_path = self.cat_image.path
            img = Image.open(img_path)

            img.thumbnail((300, 300), Image.Resampling.LANCZOS)

            img.save(img_path)


    def __str__(self):
        return self.category_name
    