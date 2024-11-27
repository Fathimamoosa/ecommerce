from django.shortcuts import render, get_object_or_404, redirect
from products.models import Products
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from products.models import Variant
from .models import Cart, CartItem
from django.contrib import messages
from django.db.models import F, Sum

def cart_summary(request):
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
        'cart/cart_summary.html', 
        {
            'cart_items': cart_items,
            'total_price': total_price,
        }
    )

    

def cart_delete(request, variant_id):
    variant = Variant.objects.get(id=variant_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(variant=variant, cart__cart_id=request.user.id)

    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(variant=variant, cart=cart)

    cart_item.delete()
    return redirect("cart_summary")

    
def delete(self, variant):
    { '4': 3, '2':1 }
    variant_id =str(variant)
    if variant_id in self.cart:
        del self.cart[variant_id]


def cart_update(request):
    pass


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart



def add_cart(request, variant_id):
    variant = Variant.objects.get(id=variant_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(cart_id=request.user.id)
        cart_item, created = CartItem.objects.get_or_create(
            variant=variant,
            cart=cart,  
            defaults={'quantity': 1},
        )
        if not created:
            if cart_item.quantity < variant.stock:
                if cart_item.quantity < 3:
                    cart_item.quantity += 1
                    cart_item.save()
                else:
                    messages.error(request, "Maximum 3 quantity per product is allowed for a user")
                    return redirect("cart_summary")
            else:
                messages.error(request, "No more stocks available")
                return redirect("cart_summary")
    else:
        cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))

        cart_item, created = CartItem.objects.get_or_create(
            variant=variant,
            cart=cart,
            defaults={'quantity': 1},
        )
        if not created:
            if cart_item.quantity < variant.stock:
                if cart_item.quantity < 3:
                    cart_item.quantity += 1
                    cart_item.save()
                else:
                    messages.error(request, "Maximum 3 quantity per product is allowed for a user")
                    return redirect("cart_summary")
            else:
                messages.error(request, "No more stocks available")
                return redirect("cart_summary")

    return redirect("cart_summary")

    

def remove_from_cart(request, variant_id):
    try:
        variant = Variant.objects.get(id=variant_id)
        
        if request.user.is_authenticated:
            
            cart_item = CartItem.objects.get(variant=variant, cart__cart_id=request.user.id)
            
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(variant=variant, cart=cart)
     
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

        return redirect("cart_summary")
    except CartItem.DoesNotExist:
     
        messages.error(request, "Item not found in the cart.")
        return redirect("cart_summary")
