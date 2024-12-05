from django.shortcuts import render, get_object_or_404, redirect
from products.models import Products
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from products.models import Variant
from .models import Cart, CartItem
from django.contrib import messages
from django.db.models import F, Sum
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.timezone import now
from coupons.models import Coupon

from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from .models import Cart, CartItem, Coupon

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
    if request.method == "POST":
        try:
            variant = Variant.objects.get(id=variant_id)
            
            # Find the cart item
            if request.user.is_authenticated:
                cart_item = CartItem.objects.get(variant=variant, cart__cart_id=request.user.id)
            else:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_item = CartItem.objects.get(variant=variant, cart=cart)
            
            # Delete the cart item
            cart_item.delete()

            # Calculate updated totals
            if request.user.is_authenticated:
                cart = Cart.objects.get(cart_id=request.user.id)
            else:
                cart = Cart.objects.get(cart_id=_cart_id(request))

            total_price = sum(item.quantity * item.variant.price for item in cart.cartitem_set.all())
            total_items = cart.cartitem_set.count()

            return JsonResponse({
                "success": True,
                "cart_total_price": total_price,
                "cart_total_items": total_items,
                "message": "Item removed successfully.",
            })
        except CartItem.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "tem not found in the cart."
            })
    return JsonResponse({
        "success": False,
        "message": "Invalid request method."
    })


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


# def add_cart(request, variant_id):
#     variant = Variant.objects.get(id=variant_id)

#     if request.user.is_authenticated:
#         cart, created = Cart.objects.get_or_create(cart_id=request.user.id)
#         cart_item, created = CartItem.objects.get_or_create(
#             variant=variant,
#             cart=cart,  
#             defaults={'quantity': 1},
#         )
#         if not created:
#             if cart_item.quantity < variant.stock:
#                 if cart_item.quantity < 3:
#                     cart_item.quantity += 1
#                     cart_item.save()
#                 else:
#                     messages.error(request, "Maximum 3 quantity per product is allowed for a user")
#                     return redirect("cart_summary")
#             else:
#                 messages.error(request, "No more stocks available")
#                 return redirect("cart_summary")
#     else:
#         cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))

#         cart_item, created = CartItem.objects.get_or_create(
#             variant=variant,
#             cart=cart,
#             defaults={'quantity': 1},
#         )
#         if not created:
#             if cart_item.quantity < variant.stock:
#                 if cart_item.quantity < 3:
#                     cart_item.quantity += 1
#                     cart_item.save()
#                 else:
#                     messages.error(request, "Maximum 3 quantity per product is allowed for a user")
#                     return redirect("cart_summary")
#             else:
#                 messages.error(request, "No more stocks available")
#                 return redirect("cart_summary")

#     return redirect("cart_summary")

# def remove_from_cart(request, variant_id):
#     if request.method == "POST":
#         try:
#             variant = Variant.objects.get(id=variant_id)
            
#             if request.user.is_authenticated:
#                 cart_item = CartItem.objects.get(variant=variant, cart__cart_id=request.user.id)
#             else:
#                 cart = Cart.objects.get(cart_id=_cart_id(request))
#                 cart_item = CartItem.objects.get(variant=variant, cart=cart)
     
#             if cart_item.quantity > 1:
#                 cart_item.quantity -= 1
#                 cart_item.save()
#             else:
#                 cart_item.delete()

#             # Calculate updated totals
#             if request.user.is_authenticated:
#                 cart = Cart.objects.get(cart_id=request.user.id)
#             else:
#                 cart = Cart.objects.get(cart_id=_cart_id(request))
            
#             total_price = sum(item.quantity * item.variant.price for item in cart.cartitem_set.all())
#             total_items = cart.cartitem_set.count()

#             return JsonResponse({
#                 "success": True,
#                 "cart_total_price": total_price,
#                 "cart_total_items": total_items,
#                 "message": "Item quantity updated successfully.",
#             })
#         except CartItem.DoesNotExist:
#             return JsonResponse({
#                 "success": False,
#                 "message": "Item not found in the cart."
#             })
#     return JsonResponse({
#         "success": False,
#         "message": "Invalid request method."
#     })

# def remove_from_cart(request, variant_id):
#     try:
#         variant = Variant.objects.get(id=variant_id)
        
#         if request.user.is_authenticated:
            
#             cart_item = CartItem.objects.get(variant=variant, cart__cart_id=request.user.id)
            
#         else:
#             cart = Cart.objects.get(cart_id=_cart_id(request))
#             cart_item = CartItem.objects.get(variant=variant, cart=cart)
     
#         if cart_item.quantity > 1:
#             cart_item.quantity -= 1
#             cart_item.save()
#         else:
#             cart_item.delete()

#         return redirect("cart_summary")
#     except CartItem.DoesNotExist:
     
#         messages.error(request, "Item not found in the cart.")
#         return redirect("cart_summary")


@require_POST
def cart_update(request, cart_id):
    """
    Update the quantity of a cart item via AJAX.
    """
    data = {}
    try:
        # Retrieve the new quantity from POST data
        quantity = int(request.POST.get('quantity', 1))
        
        # Get the CartItem based on cart_id and user/session
        if request.user.is_authenticated:
            cart_item = get_object_or_404(
                CartItem,
                id=cart_id,
                cart__cart_id=request.user.id
            )
        else:
            cart = get_object_or_404(Cart, cart_id=_cart_id(request))
            cart_item = get_object_or_404(CartItem, id=cart_id, cart=cart)
        
        # Validate the new quantity
        if quantity > cart_item.variant.stock:
            data['success'] = False
            data['message'] = 'Not enough stock available.'
            data['error_type'] = 'stock_error'
        elif quantity > 3:
            data['success'] = False
            data['message'] = 'Maximum 3 quantity per product is allowed.'
            data['error_type'] = 'max_quantity_error'
        else:
            # Update the quantity
            cart_item.quantity = quantity
            cart_item.save()
            data['success'] = True
            data['message'] = 'Quantity updated successfully.'
            data['new_quantity'] = cart_item.quantity
            data['item_total_price'] = cart_item.quantity * cart_item.variant.price
        
        # Optionally, update cart totals
        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, cart_id=request.user.id)
        else:
            cart = get_object_or_404(Cart, cart_id=_cart_id(request))
        
        total_price = sum(item.quantity * item.variant.price for item in cart.cartitem_set.all())
        total_items = cart.cartitem_set.count()
        
        data.update({
            'cart_total_price': total_price,
            'cart_total_items': total_items,
        })
        
        data['success'] = data.get('success', True)
        
    except CartItem.DoesNotExist:
        data = {'success': False, 'message': 'Cart item does not exist.'}
    except ValueError:
        data = {'success': False, 'message': 'Invalid quantity.'}
    
    # Check if the request is AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(data)
    else:
        # Fallback for non-AJAX requests
        if data.get('success'):
            messages.success(request, data.get('message'))
        else:
            messages.error(request, data.get('message'))
        return redirect('cart_summary')
    
# @csrf_exempt
# def cart_update(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             cart_item_id = data.get("cart_item_id")
#             action = data.get("action")

#             cart_item = get_object_or_404(CartItem, id=cart_item_id)
#             if action == "increase":
#                 if cart_item.quantity < cart_item.variant.stock:
#                     cart_item.quantity += 1
#                     cart_item.save()
#             elif action == "decrease":
#                 if cart_item.quantity > 1:
#                     cart_item.quantity -= 1
#                     cart_item.save()
#                 else:
#                     cart_item.delete()

#             # Calculate updated totals
#             total_price = sum(item.quantity * item.variant.price for item in cart_item.cart.cartitem_set.all())
#             total_items = cart_item.cart.cartitem_set.count()

#             return JsonResponse({
#                 "success": True,
#                 "new_quantity": cart_item.quantity,
#                 "item_total_price": cart_item.quantity * cart_item.variant.price,
#                 "cart_total_price": total_price,
#                 "cart_total_items": total_items,
#             })
#         except CartItem.DoesNotExist:
#             print("Cart item not found.")
#             return JsonResponse({"success": False, "message": "Cart item not found."})
#     return JsonResponse({"success": False, "message": "Invalid request."})