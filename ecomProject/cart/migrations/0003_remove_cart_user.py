# Generated by Django 5.0.6 on 2024-11-07 05:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_cart_cart_id_cart_date_added_cartitem_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='user',
        ),
    ]
