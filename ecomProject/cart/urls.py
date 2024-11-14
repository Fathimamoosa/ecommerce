from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_summary, name = "cart_summary"),
    path('add/<int:variant_id>/', views.add_cart, name="add_to_cart"),
    path('delete/<int:variant_id>/', views.cart_delete, name = "cart_delete"),
    path('update/<int:cart_id>/', views.cart_update, name="cart_update"),
    path('remove/<int:variant_id>/', views.remove_from_cart, name='remove_from_cart'),
]