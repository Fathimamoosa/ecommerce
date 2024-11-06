from django import forms
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
import re
from .models import Address

class CustomAuthenticationForm(forms.Form):
    email = forms.EmailField(label="Email", 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email', 'autofocus': True, 'autocomplete': 'off' })
    )
    password = forms.CharField(label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password', 'autocomplete': 'off'}),
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

class EditUserForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "email": forms.TextInput(attrs={"readonly": "readonly"}),
        }


    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not re.match(r"^[a-zA-Z\s]+$", first_name):
            raise forms.ValidationError("Name can only contain letters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not re.match(r"^[a-zA-Z\s]+$", last_name):
            raise forms.ValidationError("Name can only contain letters.")
        return last_name

class AddAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ["user", "is_default"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Name"}
            ),
            "address_line1": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Address Line 1"}
            ),
            "address_line2": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Address Line 2"}
            ),
            "town": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Town"}
            ),
            "city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "City"}
            ),
            "state": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "State"}
            ),
            "pincode": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "PIN Code"}
            ),
            "contact_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Contact Number"}
            ),
        }



class CustomUserUpdateForm(UserChangeForm):
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

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['name', 'address_line1','address_line2','town', 'city', 'state', 'pincode', 'contact_number']

def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        

        if not contact_number.isdigit() or len(contact_number) != 10:
            raise ValidationError("Phone number must be a 10-digit number.")
        
        return contact_number

def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')

        if not pincode.isdigit():
            raise ValidationError("Pincode must be a numeric value.")
        
        return pincode

def clean(self):
        cleaned_data = super().clean()
        
        required_fields = ['name', 'address_line1', 'town', 'city', 'state']
        
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, "This field is required.")
        
        return cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser 
        fields = ['username', 'email', 'first_name', 'last_name']  
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set email to be disabled (non-editable)
        self.fields['email'].disabled = True
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'readonly': 'readonly'})


