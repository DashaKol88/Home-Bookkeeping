from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from .models import Transaction, Account


# Create your views here.
def index(request):
    return HttpResponse("Hello, it's my Home Bookkeeping.")


@login_required
def latest(request):
    user_account = get_object_or_404(Account, account_owner=request.user)
    transactions = Transaction.objects.filter(transaction_account=user_account).order_by('-transaction_date')[:5]
    return render(request, 'hbm/transaction.html', {'transactions': transactions})
