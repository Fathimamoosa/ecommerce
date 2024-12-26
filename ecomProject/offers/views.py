from django.shortcuts import render, redirect
from offers.models import VariantOffer, CategoryOffer
from .forms import VariantOfferForm, CategoryOfferForm


# Create your views here.

def manage_offers(request):
    variant_offers = VariantOffer.objects.filter(is_active=True)
    category_offers = CategoryOffer.objects.filter(is_active=True)
    if request.method == 'POST':
        offer_type = request.POST.get('offer_type')  
        if offer_type == 'variant':
            form = VariantOfferForm(request.POST)
        else:
            form = CategoryOfferForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('offers:offers')  
    else:
        form = VariantOfferForm()  
    context = {
        'variant_offers': variant_offers,
        'category_offers': category_offers,
        'form': form,
    }
    return render(request, 'offers/offers.html', context)