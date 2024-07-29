from django.test import TestCase
from django.contrib.auth.models import User
from portfolio.models import Account, Portfolio, Trade, Transaction
from stocks.models import Stock, Market
import datetime
from django.utils import timezone

from portfolio.serializers import *
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from rest_framework import status
from django.http import HttpRequest as Request # Import HttpRequest

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
        self.client.force_authenticate(user=self.test_user)

    def tearDown(self):
        pass

    def get_user_url(self, user_id):
        #user = reverse('portfolio:rest:user-detail', kwargs={'pk': user_id})
        url = reverse("portfolio:user-detail",kwargs={'pk': user_id})
        response = self.client.get(url)
        print(response.data['url'])
        return response.data['url']


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
                                   amount = 50000,
                                   timestamp = timezone.now())
        Trade.objects.create(date = timezone.now(),
                             stock = stock,
                             quantity = 1000,
                             price = 45,
                             operation = Trade.TRADE_TYPES['BUY'],
                             portfolio = portfolio,
                             tax = 100.5,
                             brokerage = 200.0)


class TestAccounts(SerializerTests):
    def test_create_account(self):
        url = reverse("portfolio:user-detail",kwargs={'pk': self.test_user.pk})
        response = self.client.get(url)

        url = reverse('portfolio:account-list')
        data = {'account_id': 1, 
                'name': 'Zerodha', 
                'entity': 'BRKR', 
                'user' : response.data['url'],
                'currency': 'INR'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(Account.objects.get().account_id, 1)

    def test_get_account_list(self):
        Account.objects.create(account_id=1,
                               name='Bank 1',
                               entity = 'BANK',
                               user = self.test_user,
                               currency = 'INR')
        Account.objects.create(account_id=2,
                               name='Broker 1',
                               entity = 'BRKR',
                               user = self.test_user,
                               currency = 'INR')
        url = reverse('portfolio:account-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len([account for account in response.data.get('results')]), 2)

    def test_update_account(self):
        account = Account.objects.create(account_id=1,
                               name='Bank 1',
                               entity = 'BANK',
                               user = self.test_user,
                               currency = 'INR')
        url = reverse('portfolio:account-detail', kwargs={'pk': account.pk})
        data = {'name': 'Updated name'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        account.refresh_from_db()
        self.assertEqual(account.name, 'Updated name')

    def test_delete_account(self):
        account = Account.objects.create(account_id=1,
                               name='Bank 1',
                               entity = 'BANK',
                               user = self.test_user,
                               currency = 'INR')
        url = reverse('portfolio:account-detail', args=[account.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Account.objects.count(), 0)

class TestPortfolio(SerializerTests):
    def setUp(self):
        super().setUp()
        self.account_bank = Account.objects.create(account_id=1,
                               name='Bank 1',
                               entity = 'BANK',
                               user = self.test_user,
                               currency = 'INR')
        self.account_broker = Account.objects.create(account_id=2,
                               name='Broker 1',
                               entity = 'BRKR',
                               user = self.test_user,
                               currency = 'INR')
        
    def test_create_portfolio(self):
        account_url = reverse("portfolio:account-detail",kwargs={'pk': 2})
        response = self.client.get(account_url)

        url = reverse('portfolio:portfolio-list')
        data = {'name': 'Long term investments', 
                'account': response.data['url']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Portfolio.objects.count(), 1)
        self.assertEqual(Portfolio.objects.get().name, 'Long term investments')

    def test_get_portfolio_list(self):
        Portfolio.objects.create(name='Portfolio 1', account = self.account_broker)
        Portfolio.objects.create(name='Portfolio 2', account = self.account_broker)

        url = reverse('portfolio:portfolio-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len([project for project in response.data.get('results')]), 2)

    def test_update_portfolio(self):
        portfolio = Portfolio.objects.create(name='Portfolio 1', account = self.account_broker)
        url = reverse('portfolio:portfolio-detail', args=[portfolio.id])
        data = {'name': 'Updated Portfolio name'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        portfolio.refresh_from_db()
        self.assertEqual(portfolio.name, 'Updated Portfolio name')

    def test_delete_portfolio(self):
        portfolio = Portfolio.objects.create(name='Portfolio 1', account = self.account_broker)
        url = reverse('portfolio:portfolio-detail', args=[portfolio.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Portfolio.objects.count(), 0)

class TestTransaction(SerializerTests):
    def setUp(self):
        super().setUp()
        self.account_bank = Account.objects.create(account_id=1,
                               name='Bank 1',
                               entity = 'BANK',
                               user = self.test_user,
                               currency = 'INR')
        self.account_broker = Account.objects.create(account_id=2,
                               name='Broker 1',
                               entity = 'BRKR',
                               user = self.test_user,
                               currency = 'INR')
        self.portfolio = Portfolio.objects.create(name='Portfolio 1', 
                                                  account = self.account_broker)

    def test_create_transaction(self):
        account_url = reverse("portfolio:account-detail",kwargs={'pk': 1})
        response = self.client.get(account_url)

        url = reverse('portfolio:transaction-list')
        data = {'account': response.data['url'], 
                'transaction': 'CR',
                'amount': 50000,
                'timestamp': '2024-06-08T19:50:00.000Z'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(Transaction.objects.get().amount, 50000)

    def test_get_transaction_list(self):
        Transaction.objects.create(account = self.account_broker,
                                   transaction = 'CREDIT',
                                   amount = 50000,
                                   timestamp = timezone.now())
        Transaction.objects.create(account = self.account_broker,
                                   transaction = 'DEBIT',
                                   amount = 40000,
                                   timestamp = timezone.now())
        url = reverse('portfolio:transaction-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len([project for project in response.data.get('results')]), 2)

    def test_update_transaction(self):
        transaction = Transaction.objects.create(account = self.account_broker,
                                                transaction = 'CREDIT',
                                                amount = 50000,
                                                timestamp = timezone.now())
        url = reverse('portfolio:transaction-detail', args=[transaction.id])
        data = {'amount': 60000}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transaction.refresh_from_db()
        self.assertEqual(transaction.amount, 60000)

    def test_delete_transaction(self):
        transaction = Transaction.objects.create(account = self.account_broker,
                                                transaction = 'CREDIT',
                                                amount = 50000,
                                                timestamp = timezone.now())
        url = reverse('portfolio:transaction-detail', args=[transaction.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Transaction.objects.count(), 0)


class TestTrade(SerializerTests):
    def setUp(self):
        super().setUp()
        self.account_bank = Account.objects.create(account_id=1,
                               name='Bank 1',
                               entity = 'BANK',
                               user = self.test_user,
                               currency = 'INR')
        self.account_broker = Account.objects.create(account_id=2,
                               name='Broker 1',
                               entity = 'BRKR',
                               user = self.test_user,
                               currency = 'INR')
        self.portfolio = Portfolio.objects.create(name='Portfolio 1', 
                                                  account = self.account_broker)
        
        # Create a market
        self.market = Market.objects.create(name="NSE")
        # Create a stock
        self.stock = Stock.objects.create(market=self.market,
                                     symbol = "TATASTEEL",
                                     face_value = 1,)

    def test_create_trade(self):
        pf_url = reverse("portfolio:portfolio-detail",kwargs={'pk': 1})
        response = self.client.get(pf_url)
        pf_url_str = response.data['url']

        stock_url = reverse("portfolio:stock-detail",kwargs={'pk': 1})
        response = self.client.get(stock_url)
        stock_url_str = response.data['url']

        url = reverse('portfolio:trade-list')
        data = {'timestamp': '2024-06-08T19:50:00.000Z',
                'stock': stock_url_str,
                'portfolio': pf_url_str,
                'quantity': 400,
                'price': 100,
                'operation': 'BUY',
                'tax': 100.5,
                'brokerage': 50.54}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Trade.objects.count(), 1)
        self.assertEqual(Trade.objects.get().quantity, 400)

    def test_get_trade_list(self):
        Trade.objects.create(timestamp = timezone.now(),
                            stock = self.stock,
                            portfolio= self.portfolio,
                            quantity= 400,
                            price= 100,
                            operation= 'BUY',
                            tax= 100.5,
                            brokerage= 50.54)
        Trade.objects.create(timestamp = timezone.now(),
                            stock = self.stock,
                            portfolio= self.portfolio,
                            quantity= 400,
                            price= 100.5,
                            operation= 'SELL',
                            tax= 100.5,
                            brokerage= 50.54)
        url = reverse('portfolio:trade-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len([project for project in response.data.get('results')]), 2)

    def test_update_trade(self):
        trade = Trade.objects.create(timestamp = timezone.now(),
                            stock = self.stock,
                            portfolio= self.portfolio,
                            quantity= 400,
                            price= 100,
                            operation= 'BUY',
                            tax= 100.5,
                            brokerage= 50.54)
        url = reverse('portfolio:trade-detail', args=[trade.id])
        data = {'brokerage': 54.5}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        trade.refresh_from_db()
        self.assertEqual(trade.brokerage, 54.50)

    def test_delete_trade(self):
        project = Trade.objects.create(timestamp = timezone.now(),
                            stock = self.stock,
                            portfolio= self.portfolio,
                            quantity= 400,
                            price= 100,
                            operation= 'BUY',
                            tax= 100.5,
                            brokerage= 50.54)
        url = reverse('portfolio:trade-detail', args=[project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Trade.objects.count(), 0)

class TestDividendAPI(SerializerTests):
    def setUp(self):
        super().setUp()
        self.account_bank = Account.objects.create(account_id=1,
                               name='Bank 1',
                               entity = 'BANK',
                               user = self.test_user,
                               currency = 'INR')
        
        # Create a market
        self.market = Market.objects.create(name="NSE")
        # Create a stock
        self.stock = Stock.objects.create(market=self.market,
                                     symbol = "TATASTEEL",
                                     face_value = 1,)
        
    def test_create_dividend(self):
        stock_url = reverse("portfolio:stock-detail",kwargs={'pk': 1})
        response = self.client.get(stock_url)
        stock_url_str = response.data['url']

        url = reverse('portfolio:dividend-list')
        data = {'record_date': '2024-06-08',
                'stock': stock_url_str,
                'amount': 10}
        
        response = self.client.post(url, data, format='json')
        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Dividend.objects.count(), 1)
        self.assertEqual(Dividend.objects.get().stock, self.stock)

    def test_get_dividend_list(self):
        Dividend.objects.create(record_date = datetime.datetime.today(),
                                stock = self.stock,
                                amount = 5)
        Dividend.objects.create(record_date = datetime.datetime.today(),
                                stock = self.stock,
                                amount = 10)
        url = reverse('portfolio:dividend-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len([project for project in response.data.get('results')]), 2)

    def test_update_dividend(self):
        dividend = Dividend.objects.create(record_date = datetime.datetime.today(),
                                stock = self.stock,
                                amount = 5)
        url = reverse('portfolio:dividend-detail', args=[dividend.id])
        data = {'amount': 6}
        response = self.client.patch(url, data, format='json')
        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dividend.refresh_from_db()
        self.assertEqual(dividend.amount, 6)

    def test_delete_dividend(self):
        dividend = Dividend.objects.create(record_date = datetime.datetime.today(),
                                stock = self.stock,
                                amount = 5)
        url = reverse('portfolio:dividend-detail', args=[dividend.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Dividend.objects.count(), 0)