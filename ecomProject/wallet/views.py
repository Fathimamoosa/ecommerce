from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Wallet
from .forms import AddFundsForm

@login_required
def my_wallet_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = AddFundsForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            wallet.add_funds(amount)
            messages.success(request, f"${amount} has been added to your wallet.")
            return redirect('wallet:my_wallet')
    else:
        form = AddFundsForm()

    context = {
        'wallet': wallet,
        'form': form,
    }
    return render(request, 'wallet/my_wallet.html', context)

@login_required
def wallet_history_view(request):
    wallet = Wallet.objects.get(user=request.user)
    transactions = wallet.transactions.all().order_by('-timestamp')  # Most recent first
    return render(request, 'wallet/wallet_history.html', {'transactions': transactions})
