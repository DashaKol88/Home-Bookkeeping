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
    transactions = Transaction.objects.filter(transaction_account=user_account)
    category_list = TransactionCategory.objects.all()


    transaction_type = request.GET.get("transaction_type")
    transaction_category = request.GET.get("transaction_category")
    transaction_start_date = request.GET.get("transaction_start_date")
    transaction_end_date = request.GET.get("transaction_end_date")

    if transaction_start_date and transaction_end_date:
        transaction_start_date = datetime.strptime(transaction_start_date, '%Y-%m-%d')
        transaction_end_date = datetime.strptime(transaction_end_date, '%Y-%m-%d')
        transactions = transactions.filter(transaction_date__range=[transaction_start_date, transaction_end_date])

    if transaction_type and transaction_type == "Expense":
        transactions = transactions.filter(transaction_type=0)
    elif transaction_type and transaction_type == "Income":
        transactions = transactions.filter(transaction_type=1)

    if transaction_category:
        transactions = transactions.filter(transaction_category=transaction_category)


    return render(request, 'hbm/filter.html', {'transactions': transactions, 'category_list': category_list})


@login_required
@require_http_methods(["GET"])
def transaction_statistics(request):
    account_data = get_object_or_404(Account, account_owner=request.user)
    transactions = Transaction.objects.filter(transaction_account=account_data)

    transaction_start_date = request.GET.get("transaction_start_date")
    transaction_end_date = request.GET.get("transaction_end_date")

    if transaction_start_date and transaction_end_date:
        transaction_start_date = datetime.strptime(transaction_start_date, '%Y-%m-%d')
        transaction_end_date = datetime.strptime(transaction_end_date, '%Y-%m-%d')
        transactions = transactions.filter(transaction_date__range=[transaction_start_date, transaction_end_date])

    transaction_inc_sum = transactions.filter(transaction_type=1).aggregate(overall_income=Sum('transaction_sum'))
    transaction_exp_sum = transactions.filter(transaction_type=0).aggregate(overall_expense=Sum('transaction_sum'))
    category_list = list(transactions.values('transaction_category__category_name'))
    category_name_list = [
        *set(category_list[i]['transaction_category__category_name'] for i in range(len(category_list)))]
    statistic_data = [transaction_inc_sum, transaction_exp_sum]
    for c in category_name_list:
        statistic_data.append({c: transactions.filter(transaction_category__category_name=c).aggregate(
            Sum('transaction_sum'))["transaction_sum__sum"]})

    return render(request, 'hbm/transaction_statistics.html', {"statistic_data": statistic_data})


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
