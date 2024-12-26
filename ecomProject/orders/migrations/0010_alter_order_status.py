# Generated by Django 5.0.6 on 2024-12-07 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_delete_wallet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Returned', 'Returned'), ('Arriving', 'Arriving')], default='Pending', max_length=20),
        ),
    ]
