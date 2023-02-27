from datetime import datetime
from datetime import date
import _strptime

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import TransactionForm
from .models import Transaction, Account, TransactionCategory



# users
def user_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({"Authenticated": "true"})
    else:
        return JsonResponse({"Authenticated": "false"})


def user_register(request):
    pass


@login_required(login_url='login')
def user_account(request):
    account_data = Account.objects.filter(account_owner=request.user)
    account_data = list(account_data.values('account_number', 'account_balance'))
    return JsonResponse({"Account": account_data})


# Transactions

@login_required(login_url='login')
def transaction_latest(request):
    user_account = get_object_or_404(Account, account_owner=request.user)
    transactions = Transaction.objects.filter(transaction_account=user_account).order_by('-transaction_date')
    transactions = list(
        transactions.values('transaction_date', 'transaction_type', 'transaction_category', 'transaction_sum',
                            'transaction_comment'))
    return JsonResponse({"transactions": transactions}) # 'transaction_category' отдать имя


@login_required(login_url='login')
def transaction_filter(request):
    """ Get filters:
    available filters:transactionDate, transactionType, transactionCategory, transactionStartDate + transactionEndDate
    /api/transaction/filter?transactiondate=2023-02-26 - return all user transaction on this date 2023-02-26
    /api/transaction/filter?transactiontype=Expense -
    /api/transaction/filter?transactionStartDate=2023-01-01&transactionEndDate=2023-01-05&transactioncategory=transport
    """
    user_account = get_object_or_404(Account, account_owner=request.user)
    transactiondate = request.GET.get("transactiondate")
    transactiontype = request.GET.get("transactiontype")
    transactioncategory = request.GET.get("transactioncategory")
    transactionStartDate = request.GET.get("transactionStartDate")
    transactionEndDate = request.GET.get("transactionEndDate")
    transactions = Transaction.objects.filter(transaction_account=user_account)
    if transactiondate and transactionStartDate and transactionEndDate:
        return JsonResponse(status=400, data={'status': 'false',
                                              'message': "You cannot choose to sort by day and by time range at the same time"})
    elif transactiondate:
        transactiondate = list(map(int, transactiondate.split('-')))
        transactiondate = date(transactiondate[0], transactiondate[1], transactiondate[2])
        if transactiondate <= date.today() and transactionStartDate is None and transactionEndDate is None:
            transactions = transactions.filter(transaction_date=transactiondate)
    elif transactiontype:
        if transactiontype == "Expense":
            transactions = transactions.filter(transaction_type=0)
        if transactiontype == "Income":
            transactions = transactions.filter(transaction_type=1)
    elif transactioncategory:
        category_list = list(TransactionCategory.objects.all().values('id', 'category_name'))
        transactioncategory = [category_list[i]['id'] for i in range(len(category_list)) if
                               category_list[i]['category_name'] == transactioncategory][0]
        transactions = transactions.filter(transaction_category=transactioncategory)  # 'transaction_category' отдать имя
    elif transactionStartDate and transactionEndDate:
        transactionStartDate = list(map(int, transactionStartDate.split('-')))
        transactionStartDate = date(transactionStartDate[0], transactionStartDate[1], transactionStartDate[2])
        transactionEndDate = list(map(int, transactionEndDate.split('-')))
        transactionEndDate = date(transactionEndDate[0], transactionEndDate[1], transactionEndDate[2])
        if transactionStartDate < transactionEndDate and transactionStartDate < date.today() and transactionEndDate <= date.today() and transactiondate is None:
            transactions = transactions.filter(transaction_date__range=[transactionStartDate, transactionEndDate])
    transactions = list(transactions.values())
    return JsonResponse({"transactions": transactions})


def transaction_add(request):
    if request.method == "POST":
        user_account = get_object_or_404(Account, account_owner=request.user)
        t_transaction_account = user_account
        t_transaction_type = request.POST.get("transaction_type")
        if t_transaction_type == 'Expense':
            t_transaction_type = 0
        if t_transaction_type == 'Income':
            t_transaction_type = 1
        t_transaction_category = request.POST.get("transaction_category")
        category_list = list(TransactionCategory.objects.all().values('id', 'category_name'))
        t_transaction_category = [category_list[i]['id'] for i in range(len(category_list)) if
                                  category_list[i]['category_name'] == t_transaction_category][0]
        t_transaction_date = request.POST.get("transaction_date")
        t_transaction_sum = request.POST.get("transaction_sum")
        t_transaction_comment = request.POST.get("transaction_comment")
        if t_transaction_type == 1:
            user_account.account_balance += t_transaction_sum
        else:
            user_account.account_balance -= t_transaction_sum
        user_account.save()
        transaction = Transaction(transaction_account=t_transaction_account, transaction_type=t_transaction_type,
                              transaction_category=t_transaction_category, transaction_date=t_transaction_date,
                              transaction_sum=t_transaction_sum, transaction_comment=t_transaction_comment)
        transaction.save()
        #return redirect('transaction_latest')



def transaction_delete(request, transaction_id):
    pass


# Categories

def categories(request):
    category_list = list(TransactionCategory.objects.all().values('id','category_name'))
    return JsonResponse({'data': category_list})
