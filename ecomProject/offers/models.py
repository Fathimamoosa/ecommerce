from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.


class VariantOffer(models.Model):
    variant = models.ForeignKey( 
        'products.Variant', on_delete=models.CASCADE, related_name="variant_offer"
    )
    discount_amount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.product_name} - ₹ {self.discount_amount}"


class CategoryOffer(models.Model):
    category = models.ForeignKey(
        'category.Category', on_delete=models.CASCADE, related_name="category_offer"
    )
    discount_amount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.category.name} - ₹ {self.discount_amount}"



