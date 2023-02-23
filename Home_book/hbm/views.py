from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from .forms import TransactionForm
from .models import Transaction, Account


# Create your views here.
def index(request):
    return HttpResponse("Hello, it's my Home Bookkeeping.")


def register(request):
    if request.method != 'POST':
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return redirect('index')
    context = {'form': form}
    return render(request, 'register.html', context)


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
            if transaction.transaction_type == 1:
                user_account.account_balance += transaction.transaction_sum
            else:
                user_account.account_balance -= transaction.transaction_sum
            user_account.save()
            transaction.save()
            return redirect('latest')
    else:
        form = TransactionForm()
    return render(request, 'hbm/add_transaction.html', {"form": form})


@login_required
def del_transaction(request, transaction_id):
    user_account = get_object_or_404(Account, account_owner=request.user)
    transaction = get_object_or_404(Transaction, pk=transaction_id, transaction_account=user_account)
    if transaction.transaction_type == 1:
        user_account.account_balance -= transaction.transaction_sum
    else:
        user_account.account_balance += transaction.transaction_sum
    user_account.save()
    transaction.delete()
    return redirect('latest')
