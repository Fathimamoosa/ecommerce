from django.shortcuts import render,  get_object_or_404, redirect
from .models import Coupon
from .forms import CouponForm
from django.utils.timezone import now
from django.contrib import messages

# Create your views here.

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


# user side
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            coupon = Coupon.objects.get(code=code, active=True)
            request.session['coupon_code'] = coupon.code
            request.session['discount'] = float(coupon.discount)  
            message = "Coupon applied successfully!"
        except Coupon.DoesNotExist:
            message = "Invalid or expired coupon."
        return redirect('cart_summary')


def remove_coupon(request):
    request.session.pop('coupon_code', None)
    request.session.pop('discount', None)
    return redirect('cart_summary')

def user_coupons(request):
    coupons = Coupon.objects.filter(active=True, valid_from__Ite=now(), valid_from__gte=now())
    return render(request, 'coupons/user_coupons.html', {'coupons':coupons})

# def apply_coupon(request):
#     form = CouponForm(request.POST or None)
#     if request.method == "POST" and form.is_valid():
#         code = form.cleaned_data['code']

#         try:
#             coupon = Coupon.objects.get(code=code, active=True, valid_from__lte=now(), valid_until__gte=now())
#             request.session['coupon_id'] = coupon.id 
#             return redirect('cart') 
#         except Coupon.DoesNotExist:
#             form.add_error('code', 'Invalid or expired coupon')
#     return render(request, 'coupons/apply_coupon.html', {'form': form})

# def remove_coupon(request):
#     if 'coupon_id' in request.session:
#         del request.session['coupon_id']
#     return redirect('cart') 