from django import forms
from .models import Products, ProductImage, Variant
from .models import Review

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
        fields = ['carat', 'price', 'stock']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', ]
        widgets = {
            'rating': forms.Select(choices=[(i, str(i)) for i in range(1, 6)]),  # Rating dropdown (1-5)
            'comment': forms.Textarea(attrs={'placeholder': 'Write your review...'}),
        }