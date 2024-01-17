from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import Users, StockData, Transactions

class UsersModelTestCase(TestCase):
    def test_create_user(self):
        user = Users.objects.create(username='test_user', balance=1000)
        self.assertEqual(user.username, 'test_user')
        self.assertEqual(user.balance, 1000)

class StockDataModelTestCase(TestCase):
    def test_create_stock(self):
        stock = StockData.objects.create(ticker='AAPL', price=150.0)
        self.assertEqual(stock.ticker, 'AAPL')
        self.assertEqual(stock.price, 150.0)

class TransactionsModelTestCase(TestCase):
    def setUp(self):
        self.user = Users.objects.create(username='test_user', balance=1000)

        self.stock = StockData.objects.create(ticker='AAPL', price=150.0)

    def test_create_transaction(self):
        transaction = Transactions.objects.create(user=self.user, ticker='AAPL', transaction_type='buy', transaction_volume=5)
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.ticker, 'AAPL')
        self.assertEqual(transaction.transaction_type, 'buy')
        self.assertEqual(transaction.transaction_volume, 5)
        self.assertEqual(transaction.transaction_price, 750.0)

class UsersAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        url = '/api/users/'
        data = {'username': 'test_user', 'balance': 1000}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Users.objects.count(), 1)
        user = Users.objects.get(username='test_user')
        self.assertEqual(user.balance, 1000)

    def test_retrieve_user_data(self):
        Users.objects.create(username='test_user', balance=1000)

        url = '/api/users/test_user/'

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {'id': 1, 'username': 'test_user', 'balance': 1000, 'created_at': '...'}
        self.assertEqual(response.data, expected_data)

class StockDataAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_stock(self):
        url = '/api/stocks/'
        data = {'ticker': 'AAPL', 'price': 150.0}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(StockData.objects.count(), 1)
        stock = StockData.objects.get(ticker='AAPL')
        self.assertEqual(stock.price, 150.0)

    def test_retrieve_all_stocks(self):
        StockData.objects.create(ticker='AAPL', price=150.0)

        url = '/api/stocks/'

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = [{'ticker': 'AAPL', 'price': 150.0}]
        self.assertEqual(response.data, expected_data)

class TransactionsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = Users.objects.create(username='test_user', balance=1000)

        self.stock = StockData.objects.create(ticker='AAPL', price=150.0)

    def test_create_transaction(self):
        url = '/api/transactions/'
        data = {'user': self.user.id, 'ticker': 'AAPL', 'transaction_type': 'buy', 'transaction_volume': 5}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Transactions.objects.count(), 1)
        transaction = Transactions.objects.get(user=self.user, ticker='AAPL')
        self.assertEqual(transaction.transaction_type, 'buy')

    def test_retrieve_user_transactions(self):
        Transactions.objects.create(user=self.user, ticker='AAPL', transaction_type='buy', transaction_volume=5)

        url = f'/api/transactions/{self.user.id}/'

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = [{'id': 1, 'user': self.user.id, 'ticker': 'AAPL', 'transaction_type': 'buy', 'transaction_volume': 5, 'transaction_price': 750.0, 'timestamp': '...'}]
        self.assertEqual(response.data, expected_data)

    def test_retrieve_user_transactions_with_timestamp(self):
        Transactions.objects.create(user=self.user, ticker='AAPL', transaction_type='buy', transaction_volume=5)
        Transactions.objects.create(user=self.user, ticker='AAPL', transaction_type='sell', transaction_volume=3)

        start_timestamp = '2022-01-01T00:00:00'
        end_timestamp = '2022-01-02T00:00:00'

        url = f'/api/transactions/{self.user.id}/{start_timestamp}/{end_timestamp}/'

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = [
            {'id': 1, 'user': self.user.id, 'ticker': 'AAPL', 'transaction_type': 'buy', 'transaction_volume': 5, 'transaction_price': 750.0, 'timestamp': '...'},
            {'id': 2, 'user': self.user.id, 'ticker': 'AAPL', 'transaction_type': 'sell', 'transaction_volume': 3, 'transaction_price': 450.0, 'timestamp': '...'}
        ]
        self.assertEqual(response.data, expected_data)
