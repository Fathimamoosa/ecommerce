from django.shortcuts import render

# Create your views here.

def payment_success(request):
    return render(request, "payments/payment_success.html", {})