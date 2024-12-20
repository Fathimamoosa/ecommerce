# Generated by Django 5.0.6 on 2024-11-06 10:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_remove_profile_phone_number_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='address_line1',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='address',
            name='address_line2',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='address',
            name='contact_number',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='address',
            name='name',
            field=models.CharField(default=None, max_length=255),
        ),
        migrations.AlterField(
            model_name='address',
            name='pincode',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='address',
            name='state',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='address',
            name='town',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='address',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
