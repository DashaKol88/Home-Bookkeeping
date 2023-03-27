from datetime import datetime, date
from decimal import Decimal
from typing import Union

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Sum, FloatField
from django.http import HttpResponse, JsonResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods

from .forms import TransactionForm, PlanningTransactionForm
from .models import Transaction, Account, TransactionCategory, PlanningTransaction


# Create your views here.
def home(request: HttpRequest) -> HttpResponse:
    """
    Function for the home page with general information. If the user is logged in, the balance and username are visible.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: The rendered home page.
    :rtype: HttpResponse
    """
    if request.user.is_authenticated:
        user_account = get_object_or_404(Account, account_owner=request.user)
        return render(request, 'hbm/home.html', {'user_account': user_account})
    else:
        return render(request, 'hbm/home.html')


@require_http_methods(["POST"])
def register(request: HttpRequest) -> Union[HttpResponse, HttpResponseRedirect]:
    """
    Function for registering a new user with automatic authorization.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: If the request method is GET, renders the register.html template.
             If the request method is POST, validates the registration form and creates a new user.
             Redirects the user to the home page upon successful registration.
    :rtype: Union[HttpResponse, HttpResponseRedirect]
    """
    if request.method != 'POST':
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            new_account = Account(account_owner=request.user, account_number=0,
                                  account_balance=Decimal(0))
            new_account.save()
            return redirect('home')
    return render(request, 'hbm/register.html', {'form': form})


@login_required(login_url="/login/")
@require_http_methods(["GET"])
def latest(request: HttpRequest) -> HttpResponse:
    """
    Function for the list of recent transactions. Returns the 10 most recent transactions, sorted by date.
    :param request: The HTTP request.
    :type request: HttpRequest
    :return: The rendered HTML template for displaying the latest transactions.
    :rtype: HttpResponse
    """
    user_account = get_object_or_404(Account, account_owner=request.user)
    transactions = Transaction.objects.filter(transaction_account=user_account).order_by('-transaction_date')[:10]
    return render(request, 'hbm/transaction.html', {'transactions': transactions, 'user_account': user_account})


@login_required
@require_http_methods(["POST"])
def add_transaction(request: HttpRequest) -> Union[HttpResponse, HttpResponseRedirect]:
    """
    Function for adding a transaction. When removed, adding also changes the current balance.
    :param request: HTTP request object containing the form data.
    :type request: HttpRequest
    :return: If the request method is POST and the form is valid, redirects the user to the page with the latest
             transactions, otherwise returns a template with a form to add a transaction.
    :rtype: Union[HttpResponse, HttpResponseRedirect]
    """
    user_account = get_object_or_404(Account, account_owner=request.user)
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
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
    return render(request, 'hbm/add_transaction.html', {"form": form, 'user_account': user_account})


@login_required
@require_http_methods(["POST"])
def del_transaction(request: HttpRequest, transaction_id: int) -> HttpResponseRedirect:
    """
    Function to delete a transaction. Deleting a transaction also changes the current balance.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :param transaction_id: The ID of the transaction to delete.
    :type transaction_id: int
    :return: A redirect response to the latest transactions page.
    :rtype: HttpResponseRedirect
    """
    user_account = get_object_or_404(Account, account_owner=request.user)
    transaction = get_object_or_404(Transaction, pk=transaction_id, transaction_account=user_account)
    if transaction.transaction_type == 1:
        user_account.account_balance -= transaction.transaction_sum
    else:
        user_account.account_balance += transaction.transaction_sum
    user_account.save()
    transaction.delete()
    return redirect('latest')


@login_required
@require_http_methods(["GET"])
def filter(request: HttpRequest) -> HttpResponse:
    """
    A function to filter transactions by type, category and/or time period. Returns a filtered list of transactions.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: The HTTP response object.
    :rtype: HttpResponse
    """
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

    return render(request, 'hbm/filter.html',
                  {'transactions': transactions, 'category_list': category_list, 'user_account': user_account})


@login_required
@require_http_methods(["GET"])
def transaction_statistics(request: HttpRequest) -> HttpResponse:
    """
    Function for statistics on transactions for the selected period. Gives the total amount of income and expenses
    and the amount for each category of transactions.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: The HTTP response object.
    :rtype: HttpResponse
    """
    user_account = get_object_or_404(Account, account_owner=request.user)
    transactions = Transaction.objects.filter(transaction_account=user_account)

    transaction_start_date = request.GET.get("transaction_start_date")
    transaction_end_date = request.GET.get("transaction_end_date")

    if transaction_start_date and transaction_end_date:
        transaction_start_date = datetime.strptime(transaction_start_date, '%Y-%m-%d')
        transaction_end_date = datetime.strptime(transaction_end_date, '%Y-%m-%d')
        transactions = transactions.filter(transaction_date__range=[transaction_start_date, transaction_end_date])

    transaction_inc_sum = transactions.filter(transaction_type=1).aggregate(
        overall_income=Sum('transaction_sum', output_field=FloatField()))
    transaction_exp_sum = transactions.filter(transaction_type=0).aggregate(
        overall_expense=Sum('transaction_sum', output_field=FloatField()))
    category_list = list(transactions.values('transaction_category__category_name'))
    category_name_list = [
        *set(category_list[i]['transaction_category__category_name'] for i in range(len(category_list)))]
    statistic_data = [transaction_inc_sum, transaction_exp_sum]
    for c in category_name_list:
        statistic_data.append({c: transactions.filter(transaction_category__category_name=c).aggregate(
            Sum('transaction_sum', output_field=FloatField()))["transaction_sum__sum"]})

    return render(request, 'hbm/transaction_statistics.html',
                  {"statistic_data": statistic_data, 'user_account': user_account})


# Planning
@login_required
@require_http_methods(["GET"])
def planned_transactions(request: HttpRequest) -> HttpResponse:
    """
    Function for the list of planned transactions. Returns 10 scheduled transactions sorted by date.
    :param request: The HTTP request.
    :type request: HttpRequest
    :return: The rendered HTML template for displaying the planned transactions.
    :rtype: HttpResponse
    """
    user_account = get_object_or_404(Account, account_owner=request.user)
    transactions = PlanningTransaction.objects.filter(transaction_account_plan=user_account).order_by(
        '-transaction_date_plan')
    return render(request, 'hbm/planned_transactions.html',
                  {'transactions': transactions, 'user_account': user_account})


@login_required
@require_http_methods(["POST"])
def add_scheduled_transaction(request: HttpRequest) -> Union[HttpResponse, HttpResponseRedirect]:
    """
    Function for adding a planned transaction.
    :param request: HTTP request object containing the form data.
    :type request: HttpRequest
    :return: HTTP response object redirecting to the planned transactions page if form is valid, else renders the
        add_scheduled_transaction template.
    :rtype: Union[HttpResponse, HttpResponseRedirect]
    """
    user_account = get_object_or_404(Account, account_owner=request.user)
    if request.method == "POST":
        form = PlanningTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.transaction_account_plan = user_account
            transaction.save()
            return redirect('planned_transactions')
    else:
        form = PlanningTransactionForm()
    return render(request, 'hbm/add_scheduled_transaction.html', {"form": form, 'user_account': user_account})


@login_required
@require_http_methods(["POST"])
def del_scheduled_transaction(request: HttpRequest, transaction_id: int) -> HttpResponseRedirect:
    """
    Function to delete a planned transaction.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :param transaction_id: The ID of the transaction to be deleted.
    :type transaction_id: int
    :return: A redirect to the planned transactions page.
    :rtype: HttpResponseRedirect
    """
    user_account = get_object_or_404(Account, account_owner=request.user)
    transaction = get_object_or_404(PlanningTransaction, pk=transaction_id, transaction_account_plan=user_account)
    transaction.delete()
    return redirect('planned_transactions')


@login_required
@require_http_methods(["GET"])
def planned_transaction_statistics(request: HttpRequest) -> HttpResponse:
    """
    Function for statistics on planned transactions for the selected period. Gives the total amount of income and
    expenses and the amount for each category of transactions.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: The HTTP response object that the client will receive with the statistics of planned transactions.
    :rtype: HttpResponse
    """
    user_account = get_object_or_404(Account, account_owner=request.user)
    transactions = PlanningTransaction.objects.filter(transaction_account_plan=user_account)

    transaction_start_date = request.GET.get("transaction_start_date")
    transaction_end_date = request.GET.get("transaction_end_date")

    if transaction_start_date and transaction_end_date:
        transaction_start_date = datetime.strptime(transaction_start_date, '%Y-%m-%d')
        transaction_end_date = datetime.strptime(transaction_end_date, '%Y-%m-%d')
        transactions = transactions.filter(transaction_date_plan__range=[transaction_start_date, transaction_end_date])

    transaction_inc_sum = transactions.filter(transaction_type_plan=1).aggregate(
        planned_income=Sum('transaction_sum_plan', output_field=FloatField()))
    transaction_exp_sum = transactions.filter(transaction_type_plan=0).aggregate(
        planned_expense=Sum('transaction_sum_plan', output_field=FloatField()))

    statistic_data = [transaction_inc_sum, transaction_exp_sum]
    return render(request, 'hbm/plan_transaction_statistics.html',
                  {"statistic_data": statistic_data, 'user_account': user_account})
