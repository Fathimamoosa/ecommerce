# Generated by Django 5.0.6 on 2024-11-15 13:09

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_remove_orderitem2_order_remove_orderitem2_payment_and_more'),
        ('products', '0004_remove_products_stock_variant_stock'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Order3',
            new_name='Order',
        ),
        migrations.RenameModel(
            old_name='OrderItem3',
            new_name='OrderItem',
        ),
    ]
