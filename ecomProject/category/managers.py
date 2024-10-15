from django.db import models

class CategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class AllCategoryManager(models.Manager):
    def get_queryset(self):
        # Admin can see all categories, including soft deleted ones
        return super().get_queryset()