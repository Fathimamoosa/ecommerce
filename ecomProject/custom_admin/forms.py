from django import forms
from accounts.models import CustomUser
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from category.models import Category


class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_blocked')


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', max_length=254,
    widget=forms.TextInput(attrs={'class': 'form-control custom-class-username', 'placeholder': 'Email'}))

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control custom-class-password', 'placeholder': 'Password'})
    )                         


class CustomUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description', 'cat_image']


