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
        ('Returned', 'Returned'),
        ('Arriving', 'Arriving'),
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
    fname = models.CharField(max_length=150, null=True, blank=True)
    lname = models.CharField(max_length=150,  null=True, blank=True)
    email = models.CharField(max_length=150,  null=True, blank=True)
    phone = models.CharField(max_length=150,  null=True, blank=True)
    address = models.TextField( null=True, blank=True)
    city = models.CharField(max_length=150,  null=True, blank=True)
    state = models.CharField(max_length=150,  null=True, blank=True)
    country = models.CharField(max_length=150, null=True, blank=True)
    pincode = models.CharField(max_length=150,  null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS,null=False)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20, unique=True,blank=True)
    is_ordered = models.BooleanField(default=False)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Order {self.order_number} - {self.status}"
    class Meta:
        indexes = [
            models.Index(fields=['order_date']),
        ]
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
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return self.payment_id


class OrderProduct(models.Model):

    STATUS = (
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
        ("Return Requested", "Return Requested"),
        ("Returned", "Returned"),
    )

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="product", null=True
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
    )
    product = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    product_price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    order_item_status = models.CharField(
        max_length=20, choices=STATUS, default="Processing", null=True
    )
    final_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    def __str__(self):
        return str(self.product.product_name)

    def subtotal(self):
        return self.product_price * self.quantity
