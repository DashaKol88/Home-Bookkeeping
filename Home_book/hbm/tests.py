from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, timedelta
from .models import Account, TransactionCategory, Transaction, PlanningTransaction
from .forms import TransactionForm, PlanningTransactionForm
from django.utils import timezone


# Create your tests here.
class AccountModelTest(TestCase):
    def setUp(self):
        """
        Method called before each test case in order to set up initial data.
        This method creates a test user and an account object with some initial values.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.account = Account.objects.create(
            account_owner=self.user,
            account_number='1234567890',
            account_balance=Decimal('1000.00')
        )

    def test_account_creation(self):
        """
        This test checks that the account object was created with the correct account owner, account number, and account
        balance.
        """
        self.assertEqual(self.account.account_owner, self.user)
        self.assertEqual(self.account.account_number, '1234567890')
        self.assertEqual(self.account.account_balance, Decimal('1000.00'))

    def tearDown(self):
        """
        This method deletes the test user and account object that were created in setUp().
        """
        self.user.delete()
        self.account.delete()


class TransactionCategoryModelTest(TestCase):
    def setUp(self):
        """
        Method called before each test case in order to set up initial data.
        This method creates a test category object with some initial values.
        """
        self.category = TransactionCategory.objects.create(
            category_type=0,
            category_name='food'
        )

    def test_category_creation(self):
        """
        This test checks that the category object was created with the correct type and name.
        """
        self.assertEqual(self.category.category_type, 0)
        self.assertEqual(self.category.category_name, 'food')

    def tearDown(self):
        """
        This method deletes the test category object that was created in setUp().
        """
        self.category.delete()


class TransactionModelTest(TestCase):
    def setUp(self):
        """
        Method called before each test case in order to set up initial data.
        This method creates a test user, a test account, and a test category object.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.account = Account.objects.create(
            account_owner=self.user,
            account_number='1234567890',
            account_balance=Decimal('1000.00')
        )
        self.category = TransactionCategory.objects.create(
            category_type=0,
            category_name='food'
        )

    def test_transaction_creation(self):
        """
        This test creates a test transaction object with some initial values, and then checks that the transaction
        object was created with the correct values.
        """
        transaction = Transaction.objects.create(
            transaction_account=self.account,
            transaction_type=0,
            transaction_category=self.category,
            transaction_date=timezone.now(),
            transaction_sum=Decimal('100.00'),
            transaction_comment='Bought fruit'
        )
        self.assertEqual(transaction.transaction_account, self.account)
        self.assertEqual(transaction.transaction_type, 0)
        self.assertEqual(transaction.transaction_category, self.category)
        self.assertIsNotNone(transaction.transaction_date)
        self.assertEqual(transaction.transaction_sum, Decimal('100.00'))
        self.assertEqual(transaction.transaction_comment, 'Bought fruit')

    def tearDown(self):
        """
        This method deletes the test user, the test account, and the test category object that were created in setUp().
        """
        self.user.delete()
        self.account.delete()
        self.category.delete()


class PlanningTransactionModelTest(TestCase):
    def setUp(self):
        """
        Method called before each test case in order to set up initial data.
        This method creates a test user, a test account, and a test category object.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.account = Account.objects.create(
            account_owner=self.user,
            account_number='1234567890',
            account_balance=Decimal('1000.00')
        )
        self.category = TransactionCategory.objects.create(
            category_type=0,
            category_name='food'
        )

    def test_planning_transaction_creation(self):
        """
        This test creates a test planning transaction object with some initial values, and then checks that the planning
        transaction object was created with the correct values.
        """
        self.planning_transaction = PlanningTransaction.objects.create(
            transaction_account_plan=self.account,
            transaction_type_plan=0,
            transaction_category_plan=self.category,
            transaction_date_plan=timezone.now(),
            transaction_sum_plan=Decimal('100.00'),
            transaction_comment_plan='test comment'
        )
        self.assertEqual(self.planning_transaction.transaction_account_plan, self.account)
        self.assertEqual(self.planning_transaction.transaction_type_plan, 0)
        self.assertEqual(self.planning_transaction.transaction_category_plan, self.category)
        self.assertIsNotNone(self.planning_transaction.transaction_date_plan)
        self.assertEqual(self.planning_transaction.transaction_sum_plan, Decimal('100.00'))
        self.assertEqual(self.planning_transaction.transaction_comment_plan, 'test comment')

    def tearDown(self):
        """
        This method deletes the test user, the test account, and the test category object that were created in setUp().
        """
        self.user.delete()
        self.category.delete()
        self.account.delete()


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
