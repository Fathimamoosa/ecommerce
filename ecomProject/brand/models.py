from django.db import models
from category.managers import CategoryManager, AllCategoryManager

# Create your models here.
class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='brand_images/', blank=True, null=True)  
    objects = CategoryManager()  # For regular users
    all_objects = AllCategoryManager()  # For admin   
    is_deleted = models.BooleanField(default=False)  # Soft delete flag


    def __str__(self):
        return self.name
    