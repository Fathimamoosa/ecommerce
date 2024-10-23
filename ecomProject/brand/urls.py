from django.urls import path
from . import views

urlpatterns = [
    path('brands/', views.Brand_list, name='brand_list'),
    path('brands/create/', views.brand_create, name='brand_add'),
    path('brands/update/<int:pk>/', views.brand_update, name='brand_update'),
    path('brands/delete/<int:pk>/', views.brand_delete, name='brand_delete'),
    path('brands/restore/<int:pk>/', views.restore_brand, name='restore_brand'),
]
