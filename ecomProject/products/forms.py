from django import forms
from .models import Products, ProductImage, Variant


class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields =  "__all__"


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['products', 'image'] 

class VariantForm(forms.ModelForm):
    class Meta:
        model = Variant
        fields = ['carat', 'price']
