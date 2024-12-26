from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderItem, Payment
from django.core.paginator import Paginator
from cart.models import Cart
from django.contrib.auth.decorators import login_required
from cart.models import CartItem
import datetime
import json
from django.contrib import messages
from products.models import Variant
import uuid
from accounts.models import Address
from django.http import HttpResponse
from decimal import Decimal
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import razorpay
import tempfile
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import  CustomUser
from wallet.models import Wallet, WalletTransaction
from django.db import models
from coupons.models import Coupon
from django.db.models import Sum
from datetime import datetime
from .models import Order
from xhtml2pdf import pisa
from django.template.loader import render_to_string
client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))


# Create your views here.


def order_list(request):
    orders = Order.objects.all().order_by('-id')
    paginator = Paginator(orders, 4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number) 

    context = {
        'page_obj': page_obj,
        'orders' : orders,
    }
    return render(request, 'orders/order_list.html', context)


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart



@login_required
def place_order(request):
    if request.method == 'POST':
        user = request.user
        
        payment_method = request.POST.get('payment_method')
        shipping_address_id = request.POST.get('shipping_address')
        
        try:
            shipping_address = Address.objects.get(id=shipping_address_id, user=user)
        except Address.DoesNotExist:
            messages.error(request, "Invalid shipping address.")
            return redirect('orders:checkout')
       
        unique_order_number = str(uuid.uuid4().int)[:12]  
        new_order = Order(
            user=request.user,
            fname=request.POST.get('fname'),
            lname=request.POST.get('lname'),
            address=request.POST.get('address'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            city=request.POST.get('city'),
            country=request.POST.get('country'),
            state=request.POST.get('state'),
            pincode=request.POST.get('pincode'),
            payment_method=payment_method,
            order_number=unique_order_number
        )

        
        cart = get_object_or_404(Cart, cart_id=request.user.id)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('cart_summary')

   
        total_price = Decimal(0)
        for item in cart_items:
            variant = item.variant
            quantity = item.quantity
            price = variant.price
            
            
            if quantity > 3:
                messages.error(request, f"You can only add up to 3 quantities of {variant.product.product_name} (Carat: {variant.carat}).")
                return redirect('cart_summary')
            
            if variant.stock < quantity:
                messages.error(request, f"Insufficient stock for {variant.product.product_name} (Carat: {variant.carat}).")
                return redirect('cart_summary')
   
            variant.stock -= quantity
            variant.save()
        
            total_price += price * quantity

        new_order.total_price = total_price
        new_order.save()

        coupon_code = request.session.get('coupon_code', None)
        discount = Decimal(0)

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                discount = total_price * (coupon.discount / Decimal(100))
            except Coupon.DoesNotExist:
                discount = Decimal(0)

        total_price_after_discount = total_price - discount
        new_order.total_price_after_discount = total_price_after_discount
        new_order.save()

        if payment_method == "wallet":
            try:
                wallet = Wallet.objects.get(user=user)
                if wallet.balance < total_price_after_discount:
                    messages.error(request, "Insufficient wallet balance.")
                    return redirect('orders:checkout')
                wallet.deduct_funds(total_price_after_discount)
                WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type="payment",
                    amount=total_price_after_discount,
                    description=f"Order payment - Order No: {unique_order_number}"
                )

                new_order.status = "Confirmed"
                new_order.save()

            except Wallet.DoesNotExist:
                messages.error(request, "Wallet does not exist.")
                return redirect('orders:checkout')

        elif payment_method == "online":
            razorpay_order = client.order.create({
                "amount": int(total_price_after_discount * 100),  
                "currency": "INR",
                "payment_capture": "1"
            })
            new_order.razorpay_order_id = razorpay_order['id']
            new_order.status = "Pending"
            new_order.save()

            
            return render(request, "payments/payment.html", {
                "razorpay_key": settings.RAZORPAY_API_KEY,
                "order_id": razorpay_order['id'],
                "payment_amount": int(total_price_after_discount * 100),
                "total_price_after_discount": total_price_after_discount,
                "neworder": new_order
            })

        elif payment_method == "Cash On Delivery":
            new_order.status = "Confirmed"
            new_order.save()

        cart_items.delete()
        return redirect('orders:order_success', 
                        order_number=new_order.order_number, 
                        total_price_after_discount=str(total_price_after_discount))
    return redirect('orders:checkout')


def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, cart_id=request.user.id)
    else:
        cart_id = _cart_id(request)
        cart = get_object_or_404(Cart, cart_id=cart_id)
    cart_items = CartItem.objects.filter(cart=cart)
    for item in cart_items:
        item.sub_total = item.variant.price * item.quantity  
    
    wallet, created = Wallet.objects.get_or_create(user=request.user)

    addresses = Address.objects.filter(user=request.user).order_by('-is_default')
    total_price = sum(item.sub_total for item in cart_items)
    coupon_code = request.session.get('coupon_code', None)
    discount = Decimal(0)

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            discount = total_price * (coupon.discount / Decimal(100))
        except Coupon.DoesNotExist:
            coupon = None
            discount = Decimal(0)

    
    total_price_after_discount = total_price - discount
    return render(
        request, 
        'orders/checkout.html', 
        {   
            'addresses': addresses,
            'cart_items': cart_items,
            'total_price': total_price,
            'wallet': wallet,
            'discount': discount,
            'total_price_after_discount': total_price_after_discount,
        }
    )


def order_success(request, order_number , total_price_after_discount):
    return render(request, 'orders/success.html', {
        'order_number': order_number,
        'total_price_after_discount': total_price_after_discount
    })


def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, f"Order {order.id} status updated to {new_status}.")
        return redirect('orders:order_list')  

    return redirect('orders:order_list')

def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    print(order.items.all())
    order_items = order.items.all()
    

    for item in order_items:
        item.total_price = item.price * item.quantity

    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'orders/order_detail.html', context)

def redirect_to_payment(request):
    order_id = request.GET.get("order_id")
    if not order_id:
  
        return redirect("home")  
    
    return render(request, "orders/redirect_to_payment.html", {"order_id": order_id})

@receiver(post_save, sender=CustomUser)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ['Pending', 'Confirmed']:
        order.status = 'Cancelled'
        order.save()
        order_items = OrderItem.objects.filter(order=order)
        for order_item in order_items:
            variant = order_item.variant
            variant.stock += order_item.quantity  
            variant.save()
        order_total = order.total_price  
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        wallet.add_funds(order_total)
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='refund',
            amount=order_total,
            description=f"Refund for canceled Order #{order.id}"
        )

        messages.success(request, f'Your order has been successfully canceled and ${order_total} has been added to your wallet.')
    else:
        messages.error(request, 'Your order cannot be canceled at this stage.')

    return redirect('orders:order_detail', order_id=order.id)


@login_required
def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status != 'Delivered':
        messages.error(request, "Only delivered orders can be returned.")
        return redirect('orders:order_detail', order_id=order.id)

    
    order.status = 'returned'
    order.save()
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    wallet.add_funds(order.total_price)
    WalletTransaction.objects.create(
        wallet=wallet,
        transaction_type='refund',
        amount=order.total_price,
        description=f"Refund for returned Order #{order.id}"
    )

    messages.success(request, f"Order #{order.id} has been returned and a refund of ${order.total_price} has been credited to your wallet.")
    return redirect('orders:order_detail', order_id=order.id)

@login_required
def retry_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status != 'Pending':
        messages.error(request, "Only pending orders can be retried for payment.")
        return redirect('orders:order_detail', order_id=order.id)

    razorpay_order_data = {
        'amount': int(order.total_price * 100), 
        'currency': 'INR',
        'receipt': f'order_{order.id}',
        'payment_capture': '1'  
    }

    razorpay_order = client.order.create(razorpay_order_data)
    order.razorpay_order_id = razorpay_order['id']
    order.save()

    context = {
        'order': order,
        'razorpay_order_id': razorpay_order['id'],
        'amount': razorpay_order_data['amount'],
        "razorpay_key": settings.RAZORPAY_API_KEY,
        "order_id": razorpay_order['id'],
    }
    return render(request, 'orders/retry_payment.html', context)

# def generate_invoice(request, order_id):
#     order = get_object_or_404(Order, id=order_id, user=request.user)
#     if order.status not in ['Confirmed', 'Delivered']:
#         return HttpResponse("Invoice not available for this order.", status=403)
#     html_content = render_to_string('orders/invoice_template.html', {'order': order})
#     return HttpResponse(html_content)

def generate_invoice(request, order_id):
    order = Order.objects.get(id=order_id)

    allowed_statuses = ['confirmed', 'delivered']
    if order.status.lower() not in allowed_statuses:
        return HttpResponse("Invoice can only be generated for orders with payment status 'confirmed' or 'delivered'.")

    template_path = 'orders/invoice_template.html'
    context = {'order': order}
    html = render_to_string(template_path, context)

    # Create a Django response object and set the PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_number}.pdf"'

    # Generate PDF using xhtml2pdf
    pisa_status = pisa.CreatePDF(html, dest=response)

    # Check for errors
    if pisa_status.err:
        return HttpResponse('Error while generating PDF: <pre>' + html + '</pre>')
    return response

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        data = json.loads(request.body)
        payment_id = data['razorpay_payment_id']
        order_id = data['order_id']

        order = Order.objects.get(id=order_id)
        order.status = 'Confirmed'
        order.razorpay_payment_id = payment_id
        order.save()

        # Save payment details
        Payment.objects.create(
            user=order.user,
            payment_id=payment_id,
            payment_method="Online",
            amount_paid=order.total_price,
            status="Success",
            razorpay_order_id=order.razorpay_order_id
        )

        return JsonResponse({"message": "Payment successful"})