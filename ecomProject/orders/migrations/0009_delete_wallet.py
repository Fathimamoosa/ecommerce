# Generated by Django 5.0.6 on 2024-12-06 07:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_wallet'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Wallet',
        ),
    ]