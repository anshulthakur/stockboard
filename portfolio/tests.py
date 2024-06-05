from django.test import TestCase
from django.contrib.auth.models import User
from portfolio.models import Account, Portfolio, Trade, Transaction
from stocks.models import Stock, Market
from datetime import datetime

from portfolio.serializers import *
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from rest_framework import status

# Create your tests here.
class SerializerTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        # Create an APIClient
        self.client = APIClient()

    def tearDown(self):
        pass

    def create_portfolio(self, name):
        # Create an portfolio
        account = Account.objects.create(id=1, name="Sample Account",
                                         entity = Account.ENTITIES["BANK"],
                                         currency = "INR",
                                         user = self.user)
        # Create a portfolio
        portfolio = Portfolio.objects.create(name="Portfolio 1", 
                                             account = account)

        # Create a market
        market = Market.objects.create(name="NSE")
        # Create a stock
        stock = Stock.objects.create(market=market,
                                     symbol = "TATASTEEL",
                                     face_value = 1,)

        # Add money to account
        Transaction.objects.create(account = account,
                                   transaction = Transaction.TRANSACTION_TYPE['CR'],
                                   account = account,
                                   amount = 50000,
                                   timestamp = datetime.now())
        Trade.objects.create(date = datetime.now(),
                             stock = stock,
                             quantity = 1000,
                             price = 45,
                             operation = Trade.TRADE_TYPES['BUY'],
                             portfolio = portfolio,
                             tax = 100.5,
                             brokerage = 200.0)


class AccountTests(SerializerTests):
    def test_create_account(self):
        url = reverse('account-list')
        data = {'title': 'Project 1', 'description': 'Description for Project 1'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(Account.objects.get().title, 'Project 1')

    def test_get_account_list(self):
        Account.objects.create(title='Project 1')
        Account.objects.create(title='Project 2')
        url = reverse('account-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len([project for project in response.data.get('results')]), 2)

    def test_update_account(self):
        account = Account.objects.create(title='Project 1')
        url = reverse('account-detail', args=[account.id])
        data = {'title': 'Updated Project 1', 'description': 'Updated description'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        account.refresh_from_db()
        self.assertEqual(account.name, 'Updated Project 1')

    def test_delete_account(self):
        project = Account.objects.create(title='Project 1')
        url = reverse('account-detail', args=[project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Account.objects.count(), 0)

class PortfolioTests(SerializerTests):
    def test_create_portfolio(self):
        url = reverse('portfolio-list')
        data = {'title': 'Project 1', 'description': 'Description for Project 1'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Portfolio.objects.count(), 1)
        self.assertEqual(Portfolio.objects.get().title, 'Project 1')

    def test_get_portfolio_list(self):
        Portfolio.objects.create(title='Project 1')
        Portfolio.objects.create(title='Project 2')
        url = reverse('portfolio-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len([project for project in response.data.get('results')]), 2)

    def test_update_portfolio(self):
        portfolio = Portfolio.objects.create(title='Project 1')
        url = reverse('portfolio-detail', args=[portfolio.id])
        data = {'title': 'Updated Project 1', 'description': 'Updated description'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        portfolio.refresh_from_db()
        self.assertEqual(portfolio.name, 'Updated Project 1')

    def test_delete_portfolio(self):
        project = Portfolio.objects.create(title='Project 1')
        url = reverse('portfolio-detail', args=[project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Portfolio.objects.count(), 0)

class TransactionTests(SerializerTests):
    def test_create_transaction(self):
        url = reverse('transaction-list')
        data = {'title': 'Project 1', 'description': 'Description for Project 1'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(Transaction.objects.get().title, 'Project 1')

    def test_get_transaction_list(self):
        Transaction.objects.create(title='Project 1')
        Transaction.objects.create(title='Project 2')
        url = reverse('transaction-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len([project for project in response.data.get('results')]), 2)

    def test_update_transaction(self):
        transaction = Transaction.objects.create(title='Project 1')
        url = reverse('transaction-detail', args=[transaction.id])
        data = {'title': 'Updated Project 1', 'description': 'Updated description'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transaction.refresh_from_db()
        self.assertEqual(transaction.name, 'Updated Project 1')

    def test_delete_transaction(self):
        project = Transaction.objects.create(title='Project 1')
        url = reverse('transaction-detail', args=[project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Transaction.objects.count(), 0)


class TradeTests(SerializerTests):
    def test_create_trade(self):
        url = reverse('trade-list')
        data = {'title': 'Project 1', 'description': 'Description for Project 1'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Trade.objects.count(), 1)
        self.assertEqual(Trade.objects.get().title, 'Project 1')

    def test_get_trade_list(self):
        Trade.objects.create(title='Project 1')
        Trade.objects.create(title='Project 2')
        url = reverse('trade-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len([project for project in response.data.get('results')]), 2)

    def test_update_trade(self):
        trade = Trade.objects.create(title='Project 1')
        url = reverse('trade-detail', args=[trade.id])
        data = {'title': 'Updated Project 1', 'description': 'Updated description'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        trade.refresh_from_db()
        self.assertEqual(trade.name, 'Updated Project 1')

    def test_delete_trade(self):
        project = Trade.objects.create(title='Project 1')
        url = reverse('trade-detail', args=[project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Trade.objects.count(), 0)


class DividendTests(SerializerTests):
    def test_create_dividend(self):
        url = reverse('dividend-list')
        data = {'title': 'Project 1', 'description': 'Description for Project 1'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Dividend.objects.count(), 1)
        self.assertEqual(Dividend.objects.get().title, 'Project 1')

    def test_get_dividend_list(self):
        Dividend.objects.create(title='Project 1')
        Dividend.objects.create(title='Project 2')
        url = reverse('dividend-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len([project for project in response.data.get('results')]), 2)

    def test_update_dividend(self):
        dividend = Dividend.objects.create(title='Project 1')
        url = reverse('dividend-detail', args=[dividend.id])
        data = {'title': 'Updated Project 1', 'description': 'Updated description'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dividend.refresh_from_db()
        self.assertEqual(dividend.name, 'Updated Project 1')

    def test_delete_dividend(self):
        project = Dividend.objects.create(title='Project 1')
        url = reverse('dividend-detail', args=[project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Dividend.objects.count(), 0)