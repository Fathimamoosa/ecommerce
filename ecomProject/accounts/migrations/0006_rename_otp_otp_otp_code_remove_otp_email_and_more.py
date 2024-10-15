# Generated by Django 5.0.6 on 2024-10-10 11:46

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_rename_user_name_customuser_username'),
    ]

    operations = [
        migrations.RenameField(
            model_name='otp',
            old_name='otp',
            new_name='otp_code',
        ),
        migrations.RemoveField(
            model_name='otp',
            name='email',
        ),
        migrations.RemoveField(
            model_name='otp',
            name='resend_attempts',
        ),
        migrations.AddField(
            model_name='otp',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='otp',
            name='user',
            field=models.ForeignKey(default=django.utils.timezone.now, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
