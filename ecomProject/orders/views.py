from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderItem, Payment
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
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


# Create your views here.

client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

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
        user = request.user

        # Get the selected shipping address
        shipping_address_id = request.POST.get('shipping_address')
        try:
            shipping_address = Address.objects.get(id=shipping_address_id, user=user)
        except Address.DoesNotExist:
            messages.error(request, "Invalid shipping address.")
            return redirect('orders:checkout')
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
        neworder.order_number = unique_order_number,
        
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to place an order.")
            return redirect('login')

        cart = get_object_or_404(Cart, cart_id=request.user.id)  # Assuming a user-cart relationship
        cart_items = CartItem.objects.filter(cart=cart)
        
        for item in cart_items:
            variant = item.variant
            quantity = item.quantity

            variant.stock -= quantity
            variant.save()
            if quantity > 3:
                messages.error(
                    request,
                    f"You can only add up to 3 quantities of {variant.product.product_name} (Carat: {variant.carat})."
                )
                return redirect('cart_summary')
            
            if variant.stock < quantity:
                messages.error(request, f"Insufficient stock for {variant.product.product_name} (Carat: {variant.carat}).")
                return redirect('cart_summary')
            
        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('cart_summary')
        
        total_price = sum(item.variant.price * item.quantity for item in cart_items)
        neworder.total_price = total_price
        neworder.save()

        if neworder.payment_method == "Online payment":
            # Initiate Razorpay payment
            amount = int(total_price * 100)  # Convert to paisa
            razorpay_order = client.order.create({
                'amount': amount,
                'currency': 'INR',
                'payment_capture': '1'
            })
            neworder.razorpay_order_id = razorpay_order['id']
            neworder.save()

            # Render Razorpay payment page
            context = {
                'order': neworder,
                'razorpay_key': settings.RAZORPAY_API_KEY,
                'amount': amount,
            }
            return render(request, 'order/payment.html', context)

        elif neworder.payment_method == "Cash On Delivery":
            neworder.status = "Confirmed"

        neworder.save()
           
        neworderitems = Cart.objects.filter(cart_id=cart)
        for item in neworderitems:
            OrderItem.objects.create(
                order=neworder,
                product=item.variant.product.product_name,
                variant=item.variant.carat,  
                quantity=item.quantity,
                price=item.variant.price,
            )
            # item.variant.quantity -= item.quantity
            # item.variant.save()

            variant.stock -= quantity
            variant.save()

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
    # return render(request, 'orders/success.html', {
    #     'order_number': order_number,
    #     'total_price': total_price,
    # })
    
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
    order = get_object_or_404(Order, id=order_id)


    if order.status in ['Pending', 'Confirmed']:
        order.status = 'Cancelled'
        order.save()

    order_items = OrderItem.objects.filter(order=order)
    for order_item in order_items.all():
        variant = order_item.variant
        variant.stock += order_item.quantity  # Restore the stock
        variant.save()
        

        messages.success(request, 'Your order has been successfully canceled.')
    else:
        messages.error(request, 'Your order cannot be canceled at this stage.')

    return redirect('orders:order_detail', order_id=order.id)


@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        data = request.POST
        try:
            order = get_object_or_404(Order, razorpay_order_id=data['razorpay_order_id'])
            client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            })
            order.razorpay_payment_id = data['razorpay_payment_id']
            order.razorpay_signature = data['razorpay_signature']
            order.status = 'Confirmed'
            order.is_ordered = True
            order.save()
            # Optionally, create a payment record
            Payment.objects.create(
                user=order.user,
                payment_id=data['razorpay_payment_id'],
                amount_paid=order.total_price,
                payment_method='Online',
                status='Success',
                razorpay_order_id=order.razorpay_order_id
            )

            return redirect('orders:order_success', order_number=order.order_number, total_price=order.total_price)
        except:
            messages.error(request, "Payment verification failed.")
            return redirect('checkout')
    return redirect('/')
    #         return render(request, 'payment_success.html', {'order': order})
    #     except:
    #         return HttpResponseBadRequest()
    # return HttpResponseBadRequest()

def razorpaycheck(request):
    cart = cart.objects.filter(user=request.user)
    total_price =0
    for item in cart:
        total_price = total_price + item.product.selling_price * item.product_quantity
    return JsonResponse({
        'total_price' :total_price
    })
    
