from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from accounts.models import Variant

@receiver(post_save, sender=Order)
def update_variant_stock_on_order(sender, instance, **kwargs):
    if instance.status == 'Completed':  
        variant = instance.variant
        if variant.stock >= instance.quantity:
            variant.stock -= instance.quantity
            variant.save()
        else:
            raise ValueError("Insufficient stock to complete the order")
