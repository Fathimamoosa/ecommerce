from .models import Cart, CartItem
from .views import _cart_id
from django.db.models  import Sum

# context processor function for calculating the number of items in cart
def counter(request):
    cart_count = 0
    cart_items = []
    try:
        cart = Cart.objects.filter(cart_id=_cart_id(request))
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(cart_id=request.user.id)
        else:
            cart_items = CartItem.objects.filter(cart=cart[:1])

        for item in cart_items:
            cart_count += item.quantity
    except Cart.DoesNotExist:
        cart_items = []
    return dict(cart_count=cart_count, cart_items=cart_items)


# def cart_count(request):
#     if request.user.is_authenticated:
#         cart_items = CartItem.objects.filter(cart_id=request.user.id)
#         count = cart_items.aggregate(total=Sum('quantity'))['total'] or 0
#         return {'cart_count': count}
#     return {'cart_count': 0}