from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderItem
from django.core.paginator import Paginator
from cart.models import Cart
from django.contrib.auth.decorators import login_required
from cart.models import CartItem
import datetime
from django.contrib import messages
from products.models import Variant
import random
import uuid

# Create your views here.
def order_list(request):
    orders = Order.objects.all().order_by('id')
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
        unique_order_number = str(uuid.uuid4().int)[:12]  # 12-character unique order number
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
        neworder.order_number = unique_order_number
    
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to place an order.")
            return redirect('login')

        cart = get_object_or_404(Cart, cart_id=request.user.id)  # Assuming a user-cart relationship
        cart_items = CartItem.objects.filter(cart=cart)
        
        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('cart_summary')
        
        total_price = sum(item.variant.price * item.quantity for item in cart_items)
        neworder.total_price = total_price
        neworder.save()

        # Update status for COD
        if neworder.payment_method == "Cash On Delivery":
            neworder.status = "Confirmed"

        neworder.save()
           
        # Add items to the order
        neworderitems = Cart.objects.filter(cart_id=cart)
        for item in neworderitems:
            OrderItem.objects.create(
                order=neworder,
                product=item.variant.product.product_name,
                variant=item.variant.carat,  
                quantity=item.quantity,
                price=item.variant.price,
            )
            item.variant.quantity -= item.quantity
            item.variant.save()

        cart_items.delete()

        
        

        return redirect('orders:order_success', order_number=neworder.order_number, total_price=neworder.total_price)

    return redirect('/')


def checkout(request):
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, cart_id=request.user.id)
    else:
        cart_id = _cart_id(request)
        cart = get_object_or_404(Cart, cart_id=cart_id)
    cart_items = CartItem.objects.filter(cart=cart)
    for item in cart_items:
        item.sub_total = item.variant.price * item.quantity  
    
    total_price = sum(item.sub_total for item in cart_items)
    return render(
        request, 
        'orders/checkout.html', 
        {
            'cart_items': cart_items,
            'total_price': total_price,
        }
    )

def order_success(request, order_number, total_price):
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
