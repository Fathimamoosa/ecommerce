from django.urls import path
from . import views
from .views import DeleteImageView

app_name = 'products'

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    # path('products/product_detail1', views., name='product_detail1'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:pk>/', views.soft_delete_product, name='soft_delete_product'),
    path('products/<int:pk>/restore/', views.restore_product, name='product_restore'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/', views.product_view, name='product'),
    path('delete_image/<int:image_id>/', DeleteImageView.as_view(), name='delete_image'),
    path('wishlist/add/<int:variant_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('wishlist/remove/<int:variant_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/cart/<int:variant_id>/', views.add_to_cart_from_wishlist, name='add_to_cart_from_wishlist'),  
    # path('search/', views.search_products_view(), name='search_products'),
   ]
