from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from .forms import TransactionForm
from .models import Transaction, Account


# Create your views here.
def index(request):
    return HttpResponse("Hello, it's my Home Bookkeeping.")


@login_required
def latest(request):
    user_account = get_object_or_404(Account, account_owner=request.user)
    transactions = Transaction.objects.filter(transaction_account=user_account).order_by('-transaction_date')[:5]
    return render(request, 'hbm/transaction.html', {'transactions': transactions})


@login_required
def add_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            user_account = get_object_or_404(Account, account_owner=request.user)
            transaction.transaction_account = user_account
            user_data = Account.objects.get(account_owner=request.user)
            transaction.transaction_balance_now = user_data.account_balance
            if transaction.transaction_type == 1:
                transaction.transaction_balance_now += transaction.transaction_sum
            else:
                transaction.transaction_balance_now -= transaction.transaction_sum

            user_data.account_balance = transaction.transaction_balance_now
            user_data.save()
            transaction.save()
            return redirect('latest')
    else:
        form = TransactionForm()
    return render(request, 'hbm/add_transaction.html', {"form": form})


