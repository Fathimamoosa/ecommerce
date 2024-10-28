from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import string
import random
from datetime import timedelta
from django.contrib.auth.models import User
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length = 30, blank = True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    
# class OTP(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     otp_code = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_verified = models.BooleanField(default=False)

#     def save(self, *args, **kwargs):
#         # Generate a random 6-digit OTP
#         if not self.otp_code:
#             self.otp_code = str(random.randint(100000, 999999))
#         super().save(*args, **kwargs)

#     def is_expired(self):
#         return self.created_at + timedelta(minutes=5) < timezone.now()  # OTP expires after 5 minutes
   

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username