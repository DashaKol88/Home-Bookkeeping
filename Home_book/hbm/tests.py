from django.test import TestCase
from datetime import date, timedelta
from .forms import TransactionForm, PlanningTransactionForm


# Create your tests here.


class TransactionFormTest(TestCase):

    def test_transaction_form_date_today(self):  # проверка с сегодняшней датой
        """
        This test shows no error if the transaction date is today
        """
        date_test = date.today()
        form = TransactionForm(data={'transaction_date': date_test})
        form.is_valid()
        self.assertIsNone(form.errors.get('transaction_date'))

    def test_transaction_form_date_in_past(self):  # проверка с вчерашней датой
        """
        This test shows no error if the transaction date is in the past
        """
        date_test = date.today() - timedelta(days=1)
        form = TransactionForm(data={'transaction_date': date_test})
        form.is_valid()
        self.assertIsNone(form.errors.get('transaction_date'))

    def test_transaction_form_date_in_future(self):  # проверка с завтрашней датой
        """
        This test checks for an error message if the transaction date is in the future
        """
        date_test = date.today() + timedelta(days=1)
        form = TransactionForm(data={'transaction_date': date_test})
        self.assertFormError(form, 'transaction_date', errors=f'{date_test} is in the future')


class PlanningTransactionFormTest(TestCase):

    def test_planning_transaction_form_date_today(self):  # проверка с сегодняшней датой
        """
        This test shows no error if the transaction date is today
        """
        date_test = date.today()
        form = PlanningTransactionForm(data={'transaction_date_plan': date_test})
        form.is_valid()
        self.assertIsNone(form.errors.get('transaction_date_plan'))

    def test_planning_transaction_form_date_in_past(self):  # проверка с вчерашней датой
        """
        This test shows no error if the transaction date is in the future
        """
        date_test = date.today() - timedelta(days=1)
        form = PlanningTransactionForm(data={'transaction_date_plan': date_test})
        self.assertFormError(form, 'transaction_date_plan', errors=f'{date_test} is in the past')

    def test_planning_transaction_form_date_in_future(self):  # проверка с завтрашней датой
        """
        This test checks for an error message if the transaction date is in the past
        """
        date_test = date.today() + timedelta(days=1)
        form = PlanningTransactionForm(data={'transaction_date_plan': date_test})
        form.is_valid()
        self.assertIsNone(form.errors.get('transaction_date_plan'))
