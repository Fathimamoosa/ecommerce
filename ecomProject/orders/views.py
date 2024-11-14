from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderItem, ShippingAddress
from django.core.paginator import Paginator
from cart.models import Cart
from django.contrib.auth.decorators import login_required
from .models import Address
from cart.models import CartItem
import datetime
from django.contrib import messages
from orders.forms import ShippingForm
from orders.models import ShippingAddress




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


# def checkout(request):
#     order = Order.objects.create(order_id=request.user.id)
#     for item in order:
#                 OrderItem.objects.create(
#                     order=order,
#                     product=item['product'],
#                     quantity=item['quantity'],
#                     price=item['price']
#                 )
#     order.clear()
#     return redirect('order_confirmation', order_id=order.id)

# def checkout(request):
#     cart = Cart(request)
#     if request.method == 'POST':
#         # Create an order
#         order = Order.objects.create(
#             user=request.user,
#             total_price=cart.total_price,
#             payment_method=request.POST.get('payment_method'),
#             order_number='ORD' + str(Order.objects.count() + 1)
#         )

#         # Add cart items as order items
#         for item in cart:
#             OrderItem.objects.create(
#                 order=order,
#                 product=item['product'],
#                 variant=item.get('variant'),  # Optional
#                 quantity=item['quantity'],
#                 price=item['price']
#             )

#         cart.clear()  # Clear cart after placing the order
#         return redirect('order_confirmation', order_id=order.id)

#     return render(request, 'orders/checkout.html', {'cart': cart})



# @login_required
# def select_address(request, address_id):
#     Address.objects.filter(user=request.user).update(is_selected=False)
    
   
#     address = get_object_or_404(Address, id=address_id)
#     address.is_selected = True
#     address.save()

    
#     return redirect('checkout')


def checkout(request):
    cart = Cart(request)
    
    # Fetch the selected address for the user

    selected_address = Address.objects.filter( is_default=True).first()

    if request.method == 'POST':
        if not selected_address:
            # Handle the case where no address is selected
            return render(request, 'orders/checkout.html', {
                'cart': cart,
                'error': 'Please select an address before proceeding.',
            })

        # Create an order with the selected address
        order = Order.objects.create(
            user=request.user,
            total_price=cart.total_price,
            payment_method=request.POST.get('payment_method'),
            order_number='ORD' + str(Order.objects.count() + 1),
            address=selected_address,  # Include the selected address in the order
        )

        # Add cart items as order items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                variant=item.get('variant'),  # Optional
                quantity=item['quantity'],
                price=item['price']
            )

        cart.clear()  # Clear cart after placing the order
        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'selected_address': selected_address,
    })


# def place_order(request, total=0, quantity=0):
#     current_user =request.user

#     cart_items = CartItem.objects.filter(user=current_user)
#     cart_count = cart_items.count()

#     # if cart items is zero, redirect user to cart page
#     if cart_count <= 0:
#         return redirect("cart_summary")
    
#     quantity = 0
#     total = 0
#     for cart_item in cart_items:
#         total += cart_item.variant.price * cart_item.quantity
#         quantity += cart_item.quantity

    
#     if request.method == 'POST':
#         form= Orderform(request.POST)
#         if form.is_valid():
#             data = Order(
#                 first_name = form.cleaned_data['first_name'],
#                 last_name = form.cleaned_data['last_name'],
#                 phone = form.cleaned_data['phone'],
#                 email = form.cleaned_data['email'],
#                 address_line1 = form.cleaned_data['address_line1'],
#                 country= form.cleaned_data['country'],
#                 state = form.cleaned_data['state'],
#                 city= form.cleaned_data['city'],
#                 pincode = form.cleaned_data['pincode']
#             )
#             data.save()

#             # Generate order number
#             yr = int(datetime.date.today().strftime("%Y"))
#             dt = int(datetime.date.today().strftime("%d"))
#             mt = int(datetime.date.today().strftime("%m"))
#             d = datetime.date(yr, mt, dt)
#             current_date = d.strftime("%y%m%d")
#             order_number = current_date + str(data.id)
#             data.order_number = order_number
#             data.save()       
#             return redirect('checkout')
#         else:
#             return redirect('checkout')

def place_order(request, total=0, quantity=0):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    if not cart_items.exists():
        return redirect("cart_summary")  # Redirect if no items in the cart

    total = sum(item.variant.price * item.quantity for item in cart_items)
    quantity = sum(item.quantity for item in cart_items)

    if request.method == 'POST':
        shipping_form = ShippingForm(request.POST)
        if shipping_form.is_valid():
            # Save the shipping address
            shipping_address = shipping_form.save(commit=False)
            shipping_address.user = current_user
            shipping_address.save()

           
            order = Order.objects.create(
                user=current_user,
                total_price=total,
                is_ordered=True,
            )

    
            yr = int(datetime.date.today().strftime("%Y"))
            dt = int(datetime.date.today().strftime("%d"))
            mt = int(datetime.date.today().strftime("%m"))
            current_date = datetime.date(yr, mt, dt).strftime("%y%m%d")
            order_number = current_date + str(order.id)
            order.order_number = order_number
            order.save()

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.variant.product,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,
                    price=cart_item.variant.price,
                )

            cart_items.delete()

            return redirect('order_confirmation', order_id=order.id)
        else:
            print("Shipping Form errors:", shipping_form.errors) 

    else:
        shipping_form = ShippingForm()

    # Render the checkout page with forms
    return render(request, 'checkout.html', {'shipping_form': shipping_form, 'cart_items': cart_items, 'total': total})


# def place_order(request):
#     if request.method == 'POST':
#         # Extract data from the form
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         email = request.POST.get('email')
#         phone = request.POST.get('phone')
#         address_line1 = request.POST.get('address_line1')
#         city = request.POST.get('city')
#         state = request.POST.get('state')
#         country = request.POST.get('country')

#         # Validate required fields (additional validations can be added)
#         if not all([first_name, last_name, email, phone, address_line1, city, state, country]):
#             messages.error(request, "All fields are required.")
#             return redirect('cart')  # Redirect to the cart page

#         # Save the shipping address
#         shipping_address = ShippingAddress.objects.create(
#             user=request.user,
#             first_name=first_name,
#             last_name=last_name,
#             email=email,
#             phone=phone,
#             address_line1=address_line1,
#             city=city,
#             state=state,
#             country=country
#         )

#         # Create an order
#         order = Order.objects.create(
#             user=request.user,
#             shipping_address=shipping_address,
#             total_price=request.session.get('cart_total_price', 0)  # Fetch from session or calculate
#         )

#         # Clear cart session
#         request.session['cart_items'] = {}
#         messages.success(request, "Your order has been placed successfully!")
#         return redirect('order_success')  # Redirect to success page

#     return redirect('cart')
