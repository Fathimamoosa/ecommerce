from django import forms
from .models import VariantOffer, CategoryOffer

# Form for CategoryOffer
# class CategoryOfferForm(forms.ModelForm):
#     class Meta:
#         model = CategoryOffer
#         fields = ['offer_name', 'offer_type', 'category', 'offer_value', 'start_date', 'end_date', 'is_active']

#     def __init__(self, *args, **kwargs):
#         super(CategoryOfferForm, self).__init__(*args, **kwargs)
#         self.fields['category'].required = True  # Make 'category' required
#         self.fields['offer_value'].required = True
#         # Hide unused fields
#         if 'product' in self.fields:
#             self.fields.pop('product')


# Form for VariantOffer
# class VariantOfferForm(forms.ModelForm):
#     class Meta:
#         model = VariantOffer
#         fields = ['offer_name', 'offer_type', 'product', 'offer_value', 'start_date', 'end_date', 'is_active']

#     def __init__(self, *args, **kwargs):
#         super(VariantOfferForm, self).__init__(*args, **kwargs)
#         self.fields['product'].required = True  # Make 'product' required
#         self.fields['offer_value'].required = True
#         # Hide unused fields
#         if 'category' in self.fields:
#             self.fields.pop('category')

class VariantOfferForm(forms.ModelForm):
    class Meta:
        model = VariantOffer
        fields = ['variant', 'discount_amount', 'is_active']

class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffer
        fields = ['category', 'discount_amount', 'is_active']