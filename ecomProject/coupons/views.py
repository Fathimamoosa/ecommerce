from django.shortcuts import render,  get_object_or_404, redirect
from .models import Coupon
from .forms import CouponForm
from django.utils.timezone import now
from django.contrib import messages
from cart.views import get_cart_for_user, calculate_cart_total, _cart_id
from cart.models import Cart, CartItem
from decimal import Decimal
# Create your views here.

def available_coupons(request):
    coupons = Coupon.objects.filter(active=True, valid_from__lte=now(), valid_until__gte=now())
    return render(request, 'coupons/coupon_list.html', {'available_coupons': coupons})


def apply_selected_coupon(request, coupon_code):
    coupon = get_object_or_404(Coupon, code=coupon_code, active=True)
    cart_id = request.user.id if request.user.is_authenticated else _cart_id(request)
    cart = get_object_or_404(Cart, cart_id=cart_id)

    
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.variant.price * item.quantity for item in cart_items)

    
    if total_price >= coupon.minimum_order_amount:
        discount = total_price * (coupon.discount / Decimal(100))
        total_price_after_discount = total_price - discount

       
        request.session['coupon_code'] = coupon.code
        request.session['discount'] = float(discount)
        request.session['total_price_after_discount'] = float(total_price_after_discount)
        request.session.modified = True

        messages.success(request, f"Coupon '{coupon.code}' applied successfully!")
    else:
        messages.error(request, f"Minimum order amount for this coupon is Rs {coupon.minimum_order_amount}.")

    return redirect('cart_summary')


def admin_coupon_list(request):
    coupons = Coupon.objects.all()
    return render(request, 'accounts/coupon_list.html', {'coupons': coupons})

def admin_coupon_add(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon added successfully!')
            return redirect('admin_coupon_list')
    else:
        form = CouponForm()
    return render(request, 'accounts/coupon_form.html', {'form': form, 'action': 'Add'})


def admin_coupon_edit(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon updated successfully!')
            return redirect('admin_coupon_list')
    else:
        form = CouponForm(instance=coupon)
    return render(request, 'accounts/coupon_form.html', {'form': form, 'action': 'Edit'})


def remove_coupon(request):
    request.session.pop('coupon_code', None)
    request.session.pop('discount', None)
    return redirect('cart_summary')

def user_coupons(request):
    coupons = Coupon.objects.filter(active=True, valid_from__Ite=now(), valid_from__gte=now())
    return render(request, 'coupons/user_coupons.html', {'coupons':coupons})
