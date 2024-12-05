from django import forms
from .models import Coupon

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount', 'valid_from', 'valid_until', 'active', 'minimum_order_amount', 'maximum_discount_limit']
        widgets = {
            'valid_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'valid_until': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter coupon code'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter discount percentage'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'minimum_order_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter minimum order amount'}),
            'maximum_discount_limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter maximum discount limit'}),
        }

