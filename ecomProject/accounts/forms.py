from django import forms
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

class CustomAuthenticationForm(forms.Form):
    # email = forms.CharField(label="Username", widget=forms.TextInput(attrs={'autofocus': True}))
    # password = forms.CharField(
    #     label="Password",
    #     widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    # )
    email = forms.EmailField(
        label="Email", 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email', 'autofocus': True})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enterpassword'}),
    )
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)

            if user is None:
                raise ValidationError("Invalid email or password.")
            if user.is_blocked:
                raise ValidationError("Your account is blocked.")
        else:
            raise ValidationError("Email and password must be provided.")

        return cleaned_data



class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control','autocomplete': 'new-password'}),
        help_text=None  
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
        help_text="Enter the same password as before, for verification."  
    )
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name','last_name', 'email', 'password1', 'password2') 
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control','autocomplete': 'off'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Enter OTP',
        'class': 'form-control',
    }))

        