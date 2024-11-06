from django.shortcuts import render, get_list_or_404
from products.models import Products
from django.http import JsonResponse

# Create your views here.

def cart_summary(request):
    return render(request, "cart/cart_summary.html", {})


def cart_add(request):
    if request.POST.get('action') == 'post':
        id = int(request.POST.get(''))




def cart_delete(request):
    pass

def cart_update(request):
    pass