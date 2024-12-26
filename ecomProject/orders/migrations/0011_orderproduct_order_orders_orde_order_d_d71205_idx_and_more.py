# Generated by Django 5.0.6 on 2024-12-20 06:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_alter_order_status'),
        ('products', '0006_wishlist'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('product_price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order_item_status', models.CharField(choices=[('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Return Requested', 'Return Requested'), ('Returned', 'Returned')], default='Processing', max_length=20, null=True)),
                ('final_price', models.DecimalField(decimal_places=2, max_digits=8, null=True)),
            ],
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['order_date'], name='orders_orde_order_d_d71205_idx'),
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product', to='orders.order'),
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='payment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.payment'),
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.variant'),
        ),
    ]
