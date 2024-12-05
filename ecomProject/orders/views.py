from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderItem, Payment, Wallet
from django.core.paginator import Paginator
from cart.models import Cart
from django.contrib.auth.decorators import login_required
from cart.models import CartItem
import datetime
from django.contrib import messages
from products.models import Variant
import uuid
from accounts.models import Address
from decimal import Decimal
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import razorpay

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
        payment_method = request.POST.get("payment_method")
        total_price = request.POST.get("total_price")
        shipping_address_id = request.POST.get('shipping_address')
        try:
            shipping_address = Address.objects.get(id=shipping_address_id, user=user)
        except Address.DoesNotExist:
            messages.error(request, "Invalid shipping address.")
            return redirect('orders:checkout')
        unique_order_number = str(uuid.uuid4().int)[:12]  
        neworder =Order()
        neworder.user=request.user
        neworder.fname = request.POST.get('fname')
        neworder.lname = request.POST.get('lname')
        neworder.address = request.POST.get('address')
        neworder.phone = request.POST.get('phone')
        neworder.email = request.POST.get('email')
        neworder.city = request.POST.get('city')
        neworder.country = request.POST.get('country')
        neworder.state = request.POST.get('state')
        neworder.pincode = request.POST.get('pincode')
        neworder.payment_method = request.POST.get('payment_method')
        neworder.order_number = unique_order_number[0],

        cart = get_object_or_404(Cart, cart_id=request.user.id) 
        cart_items = CartItem.objects.filter(cart=cart)
        
        for item in cart_items:
            variant = item.variant
            quantity = item.quantity

            
            if quantity > 3:
                messages.error(
                    request,
                    f"You can only add up to 3 quantities of {variant.product.product_name} (Carat: {variant.carat})."
                )
                return redirect('cart_summary')
            
            if variant.stock < quantity:
                messages.error(request, f"Insufficient stock for {variant.product.product_name} (Carat: {variant.carat}).")
                return redirect('cart_summary')
            
            variant.stock -= quantity
            variant.save()
            
        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('cart_summary')
        
        total_price = sum(item.variant.price * item.quantity for item in cart_items)
        neworder.total_price = total_price
        neworder.save()

        if payment_method == "online":
           
            print
            razorpay_order = client.order.create({
                "amount": int(total_price * 100),  
                "currency": "INR",
                "payment_capture": "1"
            })
           
            neworder.razorpay_order_id = razorpay_order['id']
            neworder.status = "Pending"
            neworder.save()

            
            return render(request, "payments/payment.html", {
                "razorpay_key": settings.RAZORPAY_API_KEY,
                "order_id": razorpay_order['id'],
                "amount": total_price * 100,
                "total_price" : total_price,
                "neworder": neworder
            })
        
        elif neworder.payment_method == "Cash On Delivery":
            neworder.status = "Confirmed"

        neworder.save()

        cart_items.delete()

        return redirect('orders:order_success', order_number=neworder.order_number, total_price=neworder.total_price)

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
    
    addresses = Address.objects.filter(user=request.user).order_by('-is_default')
    total_price = sum(item.sub_total for item in cart_items)
    return render(
        request, 
        'orders/checkout.html', 
        {   
            'addresses': addresses,
            'cart_items': cart_items,
            'total_price': total_price,
        }
    )

def order_success(request, order_number, total_price):
    total_price = Decimal(total_price)
    
    return render(request, 'orders/success.html', {
        'order_number': order_number,
        'total_price': total_price,
    })
    
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_detail.html', {'order': order})

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


def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_id=order.id)


    if order.status in ['Pending', 'Confirmed']:
        order.status = 'Cancelled'
        order.save()

    order_items = OrderItem.objects.filter(order=order)
    for order_item in order_items.all():
        variant = order_item.variant
        variant.stock += order_item.quantity  
        variant.save()
        

        messages.success(request, 'Your order has been successfully canceled.')
    else:
        messages.error(request, 'Your order cannot be canceled at this stage.')

    return redirect('orders:order_detail', order_id=order.id)

def redirect_to_payment(request):

    order_id = request.GET.get("order_id")
    if not order_id:
  
        return redirect("home")  
    
    return render(request, "orders/redirect_to_payment.html", {"order_id": order_id})