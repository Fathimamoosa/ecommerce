from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from orders.models import Order
import razorpay
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def payment_success(request):
    print('sucesspage')
    return render(request, "payments/payment_success.html", {})

def payment(request):
    if request.method == "POST":
        
        order_id = request.POST.get("order_id")
        order = Order.objects.get(id=order_id)
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_SECRET_KEY))
        payment_amount = int(order.total_price * 100)

        razorpay_order = client.order.create({
            "amount": payment_amount,
            "currency": "INR",
            "payment_capture": "1",
        })

        order.razorpay_order_id = razorpay_order['id']
        order.save()

        return render(request, 'payments/payment.html', {
            "order_id": razorpay_order['id'],
            "amount": payment_amount,
            "online_payment_amount": order.total_price,
            "user": order.user,
        })

    return redirect('home')


@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')

       
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })

         
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.is_ordered = True
            order.status = "Confirmed"
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.save()
            print('successurl')
            return render(request, 'orders/success.html', {"order_number": order.order_number, "total_price" : order.total_price})
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"error": "Payment verification failed"}, status=400)

    return redirect('home')