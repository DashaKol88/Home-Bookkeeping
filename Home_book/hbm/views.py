from datetime import datetime, date

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods

from .forms import TransactionForm, PlanningTransactionForm
from .models import Transaction, Account, TransactionCategory, PlanningTransaction


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
    transactions = Transaction.objects.filter(transaction_account=user_account).order_by('-transaction_date')[:10]
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


def home(request):
    user_account = get_object_or_404(Account, account_owner=request.user)
    return render(request, 'hbm/home.html', {'user_account': user_account})


@login_required
def filter(request):
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
        transactions = transactions.filter(
            transaction_category=transactioncategory)  # 'transaction_category' отдать имя
    elif transactionStartDate and transactionEndDate:
        transactionStartDate = list(map(int, transactionStartDate.split('-')))
        transactionStartDate = date(transactionStartDate[0], transactionStartDate[1], transactionStartDate[2])
        transactionEndDate = list(map(int, transactionEndDate.split('-')))
        transactionEndDate = date(transactionEndDate[0], transactionEndDate[1], transactionEndDate[2])
        if transactionStartDate < transactionEndDate and transactionStartDate < date.today() and transactionEndDate <= date.today() and transactiondate is None:
            transactions = transactions.filter(transaction_date__range=[transactionStartDate, transactionEndDate])
    transactions = list(
        transactions.values('transaction_date', 'transaction_type', 'transaction_category__category_name',
                            'transaction_sum',
                            'transaction_comment'))
    return JsonResponse({"transactions": transactions})


@login_required
@require_http_methods(["GET"])
def transaction_statistic(request):
    account_data = get_object_or_404(Account, account_owner=request.user)
    transactions = Transaction.objects.filter(transaction_account=account_data)

    transaction_start_date = request.GET.get("transaction_start_date")
    transaction_end_date = request.GET.get("transaction_end_date")

    if transaction_start_date and transaction_end_date:
        transaction_start_date = datetime.strptime(transaction_start_date, '%Y-%m-%d')
        transaction_end_date = datetime.strptime(transaction_end_date, '%Y-%m-%d')
        transactions = transactions.filter(transaction_date__range=[transaction_start_date, transaction_end_date])
    else:
        return JsonResponse(status=400, data={"error": "Bad request"})

    transaction_inc_sum = transactions.filter(transaction_type=1).aggregate(overall_income=Sum('transaction_sum'))
    transaction_exp_sum = transactions.filter(transaction_type=0).aggregate(overall_expense=Sum('transaction_sum'))
    category_list = list(transactions.values('transaction_category__category_name'))
    category_name_list = [*set(category_list[i]['transaction_category__category_name'] for i in range(len(category_list)))]
    statistic_data = [transaction_inc_sum, transaction_exp_sum]
    for c in category_name_list:
        statistic_data.append({c: transactions.filter(transaction_category__category_name=c).aggregate(Sum('transaction_sum'))["transaction_sum__sum"]})

    return JsonResponse({"statistic_data": statistic_data})


# Planning
@login_required
def planned_transactions(request):
    account_data = get_object_or_404(Account, account_owner=request.user)
    transactions = PlanningTransaction.objects.filter(transaction_account_plan=account_data).order_by(
        '-transaction_date_plan')
    return render(request, 'hbm/planned_transactions.html', {'transactions': transactions})


@login_required
def add_scheduled_transaction(request):
    if request.method == "POST":
        form = PlanningTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            user_account = get_object_or_404(Account, account_owner=request.user)
            transaction.transaction_account_plan = user_account
            transaction.save()
            return redirect('planned_transactions')
    else:
        form = PlanningTransactionForm()
    return render(request, 'hbm/add_scheduled_transaction.html', {"form": form})


@login_required
def del_scheduled_transaction(request, transaction_id):
    user_account = get_object_or_404(Account, account_owner=request.user)
    transaction = get_object_or_404(PlanningTransaction, pk=transaction_id, transaction_account_plan=user_account)
    transaction.delete()
    return redirect('planned_transactions')