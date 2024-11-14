from django.db import models
from django.conf import settings
from products.models import Variant
from django.utils import timezone
from accounts.models import CustomUser

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    date_added = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"Cart of {self.user.username if self.user else 'Guest'}"

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.variant
    
    def __str__(self):
        return f"{self.quantity} x {self.variant.product.product_name} ({self.variant.carat} carat)"

    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.variant.price
        super().save(*args, **kwargs)

    def sub_total(self):
        return self.variant.price * self.quantity
    
