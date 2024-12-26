from django.urls import path
from .views import *
from . import views
from django.conf import settings
from django.conf.urls.static import static


# app_name = 'custom_admin'


urlpatterns = [
    path('login/', LoginView.as_view(), name='admin_login'),
    path('logout/', LogoutView.as_view(), name='admin_logout'),
    path('dashboard/', dashboard, name = 'dashboard'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/add/', UserCreateView.as_view(), name='user_add'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('categories/<int:pk>/restore/', views.restore_category, name='category_restore'),
    path('sales-report/', views.sales_report, name='sales_report'),
    path('sales-report-pdf/', views.sales_report_pdf, name='sales_report_pdf'),
    path('sales-report-excel/', views.sales_report_excel, name='sales_report_excel'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('sales-data/', views.get_sales_data, name='sales_data'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)