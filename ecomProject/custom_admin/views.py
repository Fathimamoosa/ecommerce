from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .forms import CustomUserForm, CustomLoginForm 
from accounts.models import *
from category.models import Category
from products.models import Products
from django.utils import timezone
from .forms import CategoryForm
from orders.models import Order, OrderItem
from django.db.models import Sum, Count
import datetime, calendar
from datetime import timedelta
from django.db.models.functions import TruncMonth, TruncWeek, TruncDate
from django.http import HttpResponse
from django.http import JsonResponse
from reportlab.pdfgen import canvas
import openpyxl


def admin_check(user):
    return user.is_authenticated and user.is_staff and user.is_superuser

class LoginView(View):
    def get(self, request):
        form = CustomLoginForm()
        print('90')
        return render(request, 'custom_admin/login.html', {'form': form})

    def post(self, request):
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')  
            password = form.cleaned_data.get('password')
            print(f"Attempting to authenticate: {username} with password {password}")
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
                print(f"Authenticated user: {user.email}")
            else:
                print("Authentication failed.")
        return render(request, 'custom_admin/login.html', {'form': form})


def dashboard(request):
    total_revenue = Order.objects.filter(status="Delivered").aggregate(Sum("total_price"))["total_price__sum"] or 0
    total_orders = Order.objects.exclude(status="in_transit").count()
    total_products = Products.objects.count()
    total_users = CustomUser.objects.filter(is_active=True).count()

    
    orders_delivered = Order.objects.filter(status="delivered").count()
    orders_processing = Order.objects.filter(status="processing").count()
    orders_shipped = Order.objects.filter(status="shipped").count()
    orders_cancelled = Order.objects.filter(status="cancelled").count()

    top_products = Products.objects.annotate(
    total_quantity_sold=Sum('variants__orderitem__quantity')
    ).filter(
    ).order_by('-total_quantity_sold')[:10]

    top_categories = (
    Category.objects
    .annotate(total_quantity=Sum('products__variants__orderitem__quantity'))
    .order_by('-total_quantity')[:4]
    )
    
    context = {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_products": total_products,
        "total_users": total_users,
        "orders_delivered": orders_delivered,
        "orders_processing": orders_processing,
        "orders_shipped": orders_shipped,
        "orders_cancelled": orders_cancelled,
        "top_products": top_products,
        "top_categories": top_categories,
    }
    return render(request, "custom_admin/dashboard.html", context)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('admin_login')  

@method_decorator(user_passes_test(admin_check, login_url='admin_login'), name='dispatch')
class UserListView(View):
    def get(self, request):
        users = CustomUser.objects.all()
        return render(request, 'custom_admin/user_list.html', {'users': users})

    def post(self, request):
        action = request.POST.get('action')
        user_ids = request.POST.getlist('user_ids')

        if action == 'block':
            CustomUser.objects.filter(id__in=user_ids).update(is_blocked=True)
            messages.success(request, "Selected users have been blocked.")
        elif action == 'unblock':
            CustomUser.objects.filter(id__in=user_ids).update(is_blocked=False)
            messages.success(request, "Selected users have been unblocked.")
        else:
            messages.error(request, "Invalid action.")

        return redirect('user_list')

@method_decorator(user_passes_test(admin_check, login_url='admin_login'), name='dispatch')
class UserCreateView(View):
    def get(self, request):
        form = CustomUserForm()
        return render(request, 'custom_admin/user_form.html', {'form': form})

    def post(self, request):
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
        return render(request, 'custom_admin/user_form.html', {'form': form})

@method_decorator(user_passes_test(admin_check, login_url='admin_login'), name='dispatch')
class UserUpdateView(View):
    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        form = CustomUserForm(instance=user)
        return render(request, 'custom_admin/user_form.html', {'form': form})

    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
        return render(request, 'custom_admin/user_form.html', {'form': form})


@method_decorator(user_passes_test(admin_check, login_url='admin_login'), name='dispatch')
class UserDeleteView(View):
    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        return render(request, 'custom_admin/user_confirm_delete.html', {'user': user})

    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.delete()
        return redirect('user_list')

@user_passes_test(admin_check, login_url='admin_login')
def category_list(request):
    categories = Category.all_objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'category/category_list.html', {'categories': categories, 'form': form})


@user_passes_test(admin_check, login_url='admin_login')
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'category/form.html', {'form': form})


@user_passes_test(admin_check, login_url='admin_login')
def category_update(request, pk):
    category = get_object_or_404(Category.all_objects, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category/category_form.html', {'form': form})

@user_passes_test(admin_check, login_url='admin_login')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.is_deleted = False
        category.save()
        category.delete()
        return redirect('category_list')
    return render(request, 'category/category_confirm_delete.html', {'category': category})


@user_passes_test(admin_check, login_url='admin_login')
def restore_category(request, pk):
    category = get_object_or_404(Category.all_objects, pk=pk)
    if request.method == 'POST':
        category.is_deleted = False
        category.save()
        return redirect('category_list')  
    return render(request, 'custom_admin/restore_confirmation.html', {'category': category})

def sales_report(request):
    orders = Order.objects.filter(is_ordered=True).order_by('-order_date')
    total_order_amount = orders.aggregate(total=models.Sum('total_price'))['total'] or 0
    total_sales_count = Order.objects.count()
    

    filter_type = request.GET.get('filter', 'overall')  
    start_date = request.GET.get('start_date') 
    end_date = request.GET.get('end_date')    

    
    today = timezone.now().date()
    current_week_start = today - timedelta(days=today.weekday()) 
    current_month_start = today.replace(day=1)                    
    current_year_start = today.replace(month=1, day=1)            

    
    if filter_type == 'daily':
        orders = Order.objects.filter(order_date__date=today)
    elif filter_type == 'weekly':
        orders = Order.objects.filter(order_date__date__gte=current_week_start)
    elif filter_type == 'monthly':
        orders = Order.objects.filter(order_date__date__gte=current_month_start)
    elif filter_type == 'yearly':
        orders = Order.objects.filter(order_date__date__gte=current_year_start)
    elif filter_type == 'custom' and start_date and end_date:
        orders = Order.objects.filter(order_date__range=[start_date, end_date])
    else:
        orders = Order.objects.all()

    context = {
        'orders': orders,
        'total_order_amount': total_order_amount,
        'total_sales_count': total_sales_count,
        'filter_type': filter_type,
        'start_date': start_date,
        'end_date': end_date,
        

    }
    return render(request, 'custom_admin/sales_report.html', context)




def sales_report_pdf(request):
    filter_type = request.GET.get('filter', 'overall')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Apply filter based on the selected filter type
    today = timezone.now().date()
    if filter_type == 'daily':
        orders = Order.objects.filter(order_date__date=today)
    elif filter_type == 'weekly':
        current_week_start = today - timedelta(days=today.weekday()) 
        orders = Order.objects.filter(order_date__date__gte=current_week_start)
    elif filter_type == 'monthly':
        current_month_start = today.replace(day=1)
        orders = Order.objects.filter(order_date__date__gte=current_month_start)
    elif filter_type == 'yearly':
        current_year_start = today.replace(month=1, day=1)
        orders = Order.objects.filter(order_date__date__gte=current_year_start)
    elif filter_type == 'custom' and start_date and end_date:
        orders = Order.objects.filter(order_date__range=[start_date, end_date])
    else:
        orders = Order.objects.filter(is_ordered=True).order_by('-order_date')

    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{datetime.date.today()}.pdf"'

    pdf = canvas.Canvas(response)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, 800, "Sales Report")

    # Table Header
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 750, "Order ID")
    pdf.drawString(150, 750, "Customer Name")
    pdf.drawString(300, 750, "Date")
    pdf.drawString(450, 750, "Total Price")

    y = 730  # Y-axis position to start the content

    # Add order data to the PDF
    pdf.setFont("Helvetica", 10)
    for order in orders:
        pdf.drawString(50, y, str(order.order_number))
        pdf.drawString(150, y, f"{order.user.email if order.user else 'Guest User'}")
        pdf.drawString(300, y, str(order.order_date))
        pdf.drawString(450, y, str(order.total_price))
        y -= 20

        if y < 50:
            pdf.showPage()
            y = 750

    pdf.save()
    return response



def sales_report_excel(request):
    filter_type = request.GET.get('filter', 'overall')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

  
    today = timezone.now().date()
    if filter_type == 'daily':
        orders = Order.objects.filter(order_date__date=today)
    elif filter_type == 'weekly':
        current_week_start = today - timedelta(days=today.weekday())
        orders = Order.objects.filter(order_date__date__gte=current_week_start)
    elif filter_type == 'monthly':
        current_month_start = today.replace(day=1)
        orders = Order.objects.filter(order_date__date__gte=current_month_start)
    elif filter_type == 'yearly':
        current_year_start = today.replace(month=1, day=1)
        orders = Order.objects.filter(order_date__date__gte=current_year_start)
    elif filter_type == 'custom' and start_date and end_date:
        orders = Order.objects.filter(order_date__range=[start_date, end_date])
    else:
        orders = Order.objects.filter(is_ordered=True).order_by('-order_date')

    
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Sales Report"

    # Adding headers
    headers = ['Order Date', 'Customer', 'Order Number', 'Total Order Amount']
    worksheet.append(headers)

    # Adding order data
    for order in orders:
        worksheet.append([
            order.order_date.strftime("%Y-%m-%d"),
            order.user.email if order.user else "Guest User",
            order.order_number,
            order.total_price,
        ])

    # Prepare the response for Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=sales_report.xlsx'
    workbook.save(response)
    return response



def get_sales_data(request):
    filter_type = request.GET.get("filter", "weekly")  # Default to weekly if no filter is provided
    now = timezone.localtime(timezone.now())  # Get current time

    orders = Order.objects.filter(status="Delivered")  # Filter for delivered orders

    if filter_type == "yearly":
        # Group by month for the current year
        sales = (
            orders.filter(order_date__year=now.year)
            .annotate(period=TruncMonth("order_date"))
            .values("period")
            .annotate(total_sales=Sum("total_price"))
            .order_by("period")
        )
        labels = [calendar.month_name[i] for i in range(1, 13)]
        
        period_map = {i: 0 for i in range(1, 13)}
        for sale in sales:
            month = sale["period"].month 
            period_map[month] = float(sale["total_sales"])

        data = [period_map[month] for month in range(1, 13)]

    elif filter_type == "monthly":
        start_date = now.replace(day=1)  
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)  
        sales = (
            orders.filter(order_date__range=(start_date, end_date))
            .annotate(period=TruncWeek("order_date"))  
            .values("period")
            .annotate(total_sales=Sum("total_price"))
            .order_by("period")
        )

 
        labels = []
        period_map = {}
        current = start_date

        while current <= end_date:
            
            week_end = min(current + timedelta(days=6), end_date)

         
            label = f"{current.strftime('%d %b')} - {week_end.strftime('%d %b')}"
            labels.append(label)

            # Initialize period_map with the exact start dates that match TruncWeek results
            period_map[current] = 0
            current += timedelta(days=7)  # Move to the next week

        # Update period_map with actual sales data
        for sale in sales:
            period_key = sale["period"]
            if isinstance(period_key, timezone.datetime):
                period_key = period_key.date()

            # Adjust matching by aligning the exact start dates of weeks
            for week_start in period_map.keys():
                week_end = week_start + timedelta(days=6)
                # Check if period_key falls within this week range
                if week_start.date() <= period_key <= week_end.date():
                    period_map[week_start] = float(sale["total_sales"])

        # Ensure data aligns with labels
        data = [period_map[key] for key in sorted(period_map.keys())]

    else:  # Weekly
        # Group by day for the last 7 days
        end_date = now.date()
        start_date = end_date - timedelta(days=6)
        sales = (
            orders.filter(order_date__range=(start_date, end_date + timedelta(days=1)))
            .annotate(period=TruncDate("order_date"))
            .values("period")
            .annotate(total_sales=Sum("total_price"))
            .order_by("period")
        )
        labels = [
            (start_date + timedelta(days=i)).strftime("%a, %d %b") for i in range(7)
        ]
        period_map = {start_date + timedelta(days=i): 0 for i in range(7)}

        # Update period_map with actual sales data
        for sale in sales:
            period_key = sale["period"]
            if isinstance(period_key, timezone.datetime):
                period_key = period_key.date()

            if period_key in period_map:
                period_map[period_key] = float(sale["total_sales"])

        # Ensure data aligns with labels
        data = [period_map[key] for key in sorted(period_map.keys())]

    return JsonResponse(
        {
            "labels": labels,
            "data": data,
        }
    )

