# Generated by Django 5.0.6 on 2024-11-04 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_rename_products_variant_product_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='variant',
            name='stock',
        ),
        migrations.AddField(
            model_name='products',
            name='stock',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
