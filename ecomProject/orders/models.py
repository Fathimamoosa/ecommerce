from django.db import models
from products.models import Products, Variant 
from accounts.models import  CustomUser



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

    order_id = models.CharField(max_length=250, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    fname = models.CharField(max_length=150, null=False)
    lname = models.CharField(max_length=150, null=False)
    email = models.CharField(max_length=150, null=False)
    phone = models.CharField(max_length=150, null=False)
    address = models.TextField(null=False)
    city = models.CharField(max_length=150, null=False)
    state = models.CharField(max_length=150, null=False)
    country = models.CharField(max_length=150, null=False)
    pincode = models.CharField(max_length=150, null=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS,null=False)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20, unique=True,blank=True)
    is_ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.order_number} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    payment =models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.variant.product.name} (x{self.quantity})"



class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=50, null=True)
    payment_method = models.CharField(max_length=50)
    amount_paid = models.CharField(max_length=50)
    status = models.CharField(max_length=100)


    def __str__(self):
        return self.payment_id



