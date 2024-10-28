from django.db import models
from category.managers import CategoryManager, AllCategoryManager

# Create your models here.
class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='brand_images/', blank=True, null=True) 
    is_deleted = models.BooleanField(default=False)  
    objects = CategoryManager()  # For regular users
    all_objects = AllCategoryManager()  # For admin   


    def __str__(self):
        return self.name
    
    def delete(self):
        self.is_deleted = True
        self.save()