# Generated by Django 5.0.6 on 2024-11-07 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0004_cartitem_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='user',
        ),
        migrations.AddField(
            model_name='cartitem',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
