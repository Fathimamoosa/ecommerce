from django.db import models
from products.models import Products, Variant 
from accounts.models import Address, CustomUser


class Order(models.Model):
    """
    Model to store order details.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_METHODS = [
        ("Online", "Online"),
        ("Cash On Delivery", "Cash On Delivery"),
        ("Wallet", "Wallet"),
        ("Wallet with Online Payment", "Wallet with Online Payment"),
    ]

    order_id = models.CharField(max_length=250, blank=True, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS,null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20, unique=True)
    is_ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.order_number} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.SET_NULL, null=True, blank=True)  # If you have variants
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    payment =models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True,null=True)
   
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.variant.product.name} (x{self.quantity})"



class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50)
    amount_paid = models.CharField(max_length=50)
    status = models.CharField(max_length=100)


    def __str__(self):
        return self.payment_id

class ShippingAddress(models.Model):
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.IntegerField(null=True)
    pincode = models.IntegerField(null=True)
    address_line1 = models.TextField(null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100,null=True)
    country = models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "shipping Address"

    def __str__(self):
        return f'shipping Address -{str(self.id)}'

