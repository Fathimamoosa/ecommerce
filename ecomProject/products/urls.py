from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:pk>/', views.soft_delete_product, name='soft_delete_product'),
    path('products/<int:pk>/restore/', views.restore_product, name='product_restore'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
]