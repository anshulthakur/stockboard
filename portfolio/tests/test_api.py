from django.test import TestCase
from django.contrib.auth.models import User
from portfolio.models import Account, Portfolio, Trade, Transaction
from stocks.models import Stock, Market, Company
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

class TestAccounts(SerializerTests):
    def test_create_account(self):
        url = reverse("portfolio:user-detail",kwargs={'pk': self.test_user.pk})
        response = self.client.get(url)

        url = reverse('portfolio:account-list')
        print(url)
        data = {'account_id': 1, 
                'name': 'Canara', 
                'entity': 'BANK', 
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
        acc = Account.objects.create(account_id=2,
                               name='Demat 1',
                               entity = 'DMAT',
                               user = self.test_user,
                               currency = 'INR')
        acc.refresh_from_db()

        Account.objects.create(account_id=3,
                               name='Broker 1',
                               entity = 'BRKR',
                               user = self.test_user,
                               currency = 'INR',
                               linked_demat_account = acc)
        
        url = reverse('portfolio:account-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len([account for account in response.data.get('results')]), 3)

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
        self.account_demat = Account.objects.create(account_id=2,
                               name='Demat 1',
                               entity = 'DMAT',
                               user = self.test_user,
                               currency = 'INR')
        self.account_broker = Account.objects.create(account_id=3,
                               name='Broker 1',
                               entity = 'BRKR',
                               user = self.test_user,
                               currency = 'INR',
                               linked_demat_account = self.account_demat)
        
    def test_create_portfolio(self):
        account_url = reverse("portfolio:account-detail",kwargs={'pk': 3})
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
        self.account_demat = Account.objects.create(account_id=2,
                               name='Demat 1',
                               entity = 'DMAT',
                               user = self.test_user,
                               currency = 'INR')
        self.account_broker = Account.objects.create(account_id=3,
                               name='Broker 1',
                               entity = 'BRKR',
                               user = self.test_user,
                               currency = 'INR',
                               linked_demat_account = self.account_demat)
        self.portfolio = Portfolio.objects.create(name='Portfolio 1', 
                                                  account = self.account_broker)

    def test_create_transaction(self):
        account_url = reverse("portfolio:account-detail",kwargs={'pk': 1})
        response = self.client.get(account_url)

        url = reverse('portfolio:transaction-list')
        data = {'destination_account': response.data['url'], 
                'transaction_type': 'CR',
                'amount': 50000,
                'timestamp': '2024-06-08T19:50:00.000Z',
                'notes': 'Initial deposit'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(Transaction.objects.get().amount, 50000)

    def test_get_transaction_list(self):
        Transaction.objects.create(destination_account = self.account_bank,
                                   transaction_type = 'CR',
                                   amount = 50000,
                                   timestamp = timezone.now())
        Transaction.objects.create(source_account = self.account_bank,
                                   destination_account = self.account_broker,
                                   transaction_type = 'TR',
                                   amount = 40000,
                                   timestamp = timezone.now())
        url = reverse('portfolio:transaction-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len([project for project in response.data.get('results')]), 2)

    def test_update_transaction(self):
        transaction = Transaction.objects.create(destination_account = self.account_bank,
                                                transaction_type = 'CR',
                                                amount = 50000,
                                                timestamp = timezone.now())
        url = reverse('portfolio:transaction-detail', args=[transaction.id])
        data = {'amount': 60000}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transaction.refresh_from_db()
        self.assertEqual(transaction.amount, 60000)

    def test_delete_transaction(self):
        transaction = Transaction.objects.create(destination_account = self.account_bank,
                                                transaction_type = 'CR',
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
        self.account_demat = Account.objects.create(account_id=2,
                               name='Demat 1',
                               entity = 'DMAT',
                               user = self.test_user,
                               currency = 'INR')
        self.account_broker = Account.objects.create(account_id=3,
                               name='Broker 1',
                               entity = 'BRKR',
                               user = self.test_user,
                               currency = 'INR',
                               linked_demat_account = self.account_demat)
        self.portfolio = Portfolio.objects.create(name='Portfolio 1', 
                                                  account = self.account_broker)

        # Create a market
        self.market = Market.objects.create(name="NSE")
        # Create a stock
        self.stock = Stock.objects.create(market=self.market,
                                     symbol = "TATASTEEL",
                                     face_value = 1,)
        
        Transaction.objects.create(destination_account = self.account_bank,
                                   transaction_type = 'CR',
                                   amount = 50000,
                                   timestamp = timezone.now())
        Transaction.objects.create(source_account = self.account_bank,
                                   destination_account = self.account_broker,
                                   transaction_type = 'TR',
                                   amount = 40000,
                                   timestamp = timezone.now())

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
                'price': 99,
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
                            price= 99,
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
                            price= 99,
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
                            price= 99,
                            operation= 'BUY',
                            tax= 100.5,
                            brokerage= 50.54)
        url = reverse('portfolio:trade-detail', args=[project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Trade.objects.count(), 0)

class TestBulkTrade(SerializerTests):
    def setUp(self):
        super().setUp()

        # Create accounts
        self.account_bank = Account.objects.create(
            account_id=1, name='Bank 1', entity='BANK', user=self.test_user, currency='INR'
        )
        self.account_demat = Account.objects.create(
            account_id=2, name='Demat 1', entity='DMAT', user=self.test_user, currency='INR'
        )
        self.account_broker = Account.objects.create(
            account_id=3, name='Broker 1', entity='BRKR', user=self.test_user, currency='INR',
            linked_demat_account=self.account_demat
        )
        
        # Create a portfolio
        self.portfolio = Portfolio.objects.create(name='Portfolio 1', account=self.account_broker)

        # Create a market
        self.market = Market.objects.create(name="NSE")

        # Create companies and stocks
        self.company = Company.objects.create(name="Tata Steel Ltd", isin="INE081A01012")
        self.stock = Stock.objects.create(
            market=self.market, symbol="TATASTEEL", face_value=1, content_object=self.company
        )

        # Create some transactions for funding
        Transaction.objects.create(
            destination_account=self.account_bank, transaction_type='CR', amount=50000, timestamp=timezone.now()
        )
        Transaction.objects.create(
            source_account=self.account_bank, destination_account=self.account_broker, 
            transaction_type='TR', amount=40000, timestamp=timezone.now()
        )

    def test_bulk_trade_creation_with_isin(self):
        # URLs for related objects
        pf_url = reverse("portfolio:portfolio-detail", kwargs={'pk': self.portfolio.id})
        company = Company.objects.create(name="Tata Steel", isin="INE081A01012")
        
        # First, we create stock using ISIN and market
        data = [
            {
                'timestamp': '2024-06-08T19:50:00.000Z',
                'isin': 'INE081A01012',  # ISIN provided instead of stock symbol
                'exchange': self.market.name,
                'portfolio': pf_url,
                'quantity': 400,
                'price': 99,
                'operation': 'BUY',
                'tax': 100.5,
                'brokerage': 50.54,
                'trade_id': '123idjdj3303'
            },
            {
                'timestamp': '2024-06-08T20:00:00.000Z',
                'isin': 'INE081A01012',
                'exchange': self.market.name,
                'portfolio': pf_url,
                'quantity': 200,
                'price': 101,
                'operation': 'SELL',
                'tax': 50.5,
                'brokerage': 25.54,
                'trade_id': '123idjdj3387'
            }
        ]

        url = reverse('portfolio:bulk-trade-list')  # Bulk trade endpoint
        response = self.client.post(url, data, format='json')
        
        #print(response.content)
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Trade.objects.count(), 2)
        
        # Check that each trade has the correct quantity and price
        trades = Trade.objects.all()
        self.assertEqual(trades[0].quantity, 400)
        self.assertEqual(trades[0].price, 99)
        self.assertEqual(trades[1].quantity, 200)
        self.assertEqual(trades[1].price, 101)

    def test_bulk_trade_creation_with_partially_incorrect_isin(self):
        # URLs for related objects
        pf_url = reverse("portfolio:portfolio-detail", kwargs={'pk': self.portfolio.id})
        company = Company.objects.create(name="Tata Steel", isin="INE081A01012")
        
        # First, we create stock using ISIN and market
        data = [
            {
                'timestamp': '2024-06-08T19:50:00.000Z',
                'isin': 'INE081A01012',  # ISIN provided instead of stock symbol
                'exchange': self.market.name,
                'portfolio': pf_url,
                'quantity': 400,
                'price': 99,
                'operation': 'BUY',
                'tax': 100.5,
                'brokerage': 50.54,
                'trade_id': '123idjdj3303'
            },
            {
                'timestamp': '2024-06-08T20:00:00.000Z',
                'isin': 'INE081A0101',
                'exchange': self.market.name,
                'portfolio': pf_url,
                'quantity': 200,
                'price': 101,
                'operation': 'SELL',
                'tax': 50.5,
                'brokerage': 25.54,
                'trade_id': '123idjdj3387'
            }
        ]

        url = reverse('portfolio:bulk-trade-list')  # Bulk trade endpoint
        response = self.client.post(url, data, format='json')
        
        #print(response.content)
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Trade.objects.count(), 0)

    def test_bulk_trade_creation_with_partially_duplicate_values(self):
        # URLs for related objects
        pf_url = reverse("portfolio:portfolio-detail", kwargs={'pk': self.portfolio.id})
        company = Company.objects.create(name="Tata Steel", isin="INE081A01012")
        
        # First, we create stock using ISIN and market
        data = [
            {
                'timestamp': '2024-06-08T19:50:00.000Z',
                'isin': 'INE081A01012',  # ISIN provided instead of stock symbol
                'exchange': self.market.name,
                'portfolio': pf_url,
                'quantity': 400,
                'price': 99,
                'operation': 'BUY',
                'tax': 100.5,
                'brokerage': 50.54,
                'trade_id': '123idjdj3303'
            },
            {
                'timestamp': '2024-06-08T20:00:00.000Z',
                'isin': 'INE081A01012',
                'exchange': self.market.name,
                'portfolio': pf_url,
                'quantity': 200,
                'price': 101,
                'operation': 'SELL',
                'tax': 50.5,
                'brokerage': 25.54,
                'trade_id': '123idjdj3387'
            }
        ]

        url = reverse('portfolio:bulk-trade-list')  # Bulk trade endpoint
        response = self.client.post(url, data, format='json')

        # First, we create stock using ISIN and market
        data = [
            {
                'timestamp': '2024-06-08T19:50:00.000Z',
                'isin': 'INE081A01012',  # ISIN provided instead of stock symbol
                'exchange': self.market.name,
                'portfolio': pf_url,
                'quantity': 400,
                'price': 99,
                'operation': 'BUY',
                'tax': 100.5,
                'brokerage': 50.54,
                'trade_id': '123idjdj330x'
            },
            {
                'timestamp': '2024-06-08T20:00:00.000Z',
                'isin': 'INE081A01012',
                'exchange': self.market.name,
                'portfolio': pf_url,
                'quantity': 200,
                'price': 101,
                'operation': 'SELL',
                'tax': 50.5,
                'brokerage': 25.54,
                'trade_id': '123idjdj3387'
            }
        ]
        response = self.client.post(url, data, format='json')
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Trade.objects.count(), 3)
        
        # Check that each trade has the correct quantity and price
        trades = Trade.objects.all()
        self.assertEqual(trades[0].quantity, 400)
        self.assertEqual(trades[0].price, 99)
        self.assertEqual(trades[1].quantity, 200)
        self.assertEqual(trades[1].price, 101)
        self.assertEqual(trades[2].quantity, 400)
        self.assertEqual(trades[2].price, 99)

    
    def test_bulk_trade_creation_with_stock_split(self):
        # URLs for related objects
        pf_url = reverse("portfolio:portfolio-detail", kwargs={'pk': self.portfolio.id})
        company = Company.objects.create(name="Tata Steel", isin="INE081A01012")
        
        # First, we create stock using ISIN and market
        data = [
            {
                'timestamp': '2019-06-08T19:50:00.000Z',
                'isin': 'INE081A01012',  # ISIN provided instead of stock symbol
                'exchange': self.market.name,
                'portfolio': pf_url,
                'quantity': 100,
                'price': 99,
                'operation': 'BUY',
                'tax': 100.5,
                'brokerage': 50.54,
                'trade_id': '123idjdj3303'
            },
            {
                'timestamp': '2020-06-08T20:00:00.000Z',
                'isin': 'INE081A01012',
                'exchange': self.market.name,
                'portfolio': pf_url,
                'quantity': 50,
                'price': 101,
                'operation': 'SELL',
                'tax': 50.5,
                'brokerage': 25.54,
                'trade_id': '123idjdj3387'
            }
        ]

        url = reverse('portfolio:bulk-trade-list')  # Bulk trade endpoint
        response = self.client.post(url, data, format='json')
        
        #print(response.content)
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Trade.objects.count(), 3)
        
        # Check that each trade has the correct quantity and price
        trades = Trade.objects.all()
        #print(trades)
        self.assertEqual(trades[0].quantity, 100)
        self.assertEqual(trades[0].price, 99)
        self.assertEqual(trades[1].quantity, 50)
        self.assertEqual(trades[1].price, 101)
        self.assertEqual(trades[2].quantity, 450)
        self.assertEqual(trades[2].price, 0)

    def test_bulk_trade_creation_with_symbol(self):
        # Reverse URL for portfolio
        pf_url = reverse("portfolio:portfolio-detail", kwargs={'pk': self.portfolio.id})

        # Test bulk creation using stock symbol
        url = reverse('portfolio:bulk-trade-list')
        data = [
            {
                'timestamp': '2024-06-08T19:50:00.000Z',
                'stock_symbol': 'TATASTEEL',
                'exchange': self.market.name,
                'portfolio': pf_url,
                'quantity': 400,
                'price': 99,
                'operation': 'BUY',
                'tax': 100.5,
                'brokerage': 50.54,
                'trade_id': '123idjdj3303'
            },
            {
                'timestamp': '2024-06-08T20:00:00.000Z',
                'isin': 'INE081A01012',
                'exchange': self.market.name,
                'portfolio': pf_url,
                'quantity': 200,
                'price': 101,
                'operation': 'SELL',
                'tax': 50.5,
                'brokerage': 25.54,
                'trade_id': '123idjdj3387'
            }
        ]

        response = self.client.post(url, data, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Trade.objects.count(), 2)
        trades = Trade.objects.all()
        self.assertEqual(trades[0].quantity, 400)
        self.assertEqual(trades[0].price, 99)
        self.assertEqual(trades[1].quantity, 200)
        self.assertEqual(trades[1].price, 101)

    def test_bulk_trade_creation_missing_stock(self):
        # Reverse URL for portfolio
        pf_url = reverse("portfolio:portfolio-detail", kwargs={'pk': self.portfolio.id})

        # Test bulk creation with neither ISIN nor symbol provided
        url = reverse('portfolio:bulk-trade-list')
        data = {
            'timestamp': '2024-06-08T19:50:00.000Z',
            'portfolio': pf_url,
            'quantity': 500,
            'price': 120,
            'operation': 'BUY',
            'tax': 110.5,
            'brokerage': 60.75
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class TestDividendAPI(SerializerTests):
    def setUp(self):
        super().setUp()
        self.account_bank = Account.objects.create(account_id=1,
                               name='Bank 1',
                               entity = 'BANK',
                               user = self.test_user,
                               currency = 'INR')
        self.account_demat = Account.objects.create(account_id=2,
                               name='Demat 1',
                               entity = 'DMAT',
                               user = self.test_user,
                               currency = 'INR')
        self.account_broker = Account.objects.create(account_id=3,
                               name='Broker 1',
                               entity = 'BRKR',
                               user = self.test_user,
                               currency = 'INR',
                               linked_demat_account = self.account_demat)
        self.portfolio = Portfolio.objects.create(name='Portfolio 1', 
                                                  account = self.account_broker)

        # Create a market
        self.market = Market.objects.create(name="NSE")
        # Create a stock
        self.stock = Stock.objects.create(market=self.market,
                                     symbol = "TATASTEEL",
                                     face_value = 1,)
        
        Transaction.objects.create(destination_account = self.account_bank,
                                   transaction_type = 'CR',
                                   amount = 50000,
                                   timestamp = timezone.now())
        
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

class Test_Composite_Url_Apis(SerializerTests):
    def test_overview_page_query_blank_account(self):
        summary_url = reverse("portfolio:net-worth")
        response = self.client.get(summary_url)

        data = response.json()
        self.assertEqual(data.get('net_worth', -1), Decimal(0))
        self.assertEqual(data.get('net_gains', -1), Decimal(0))
        self.assertEqual(data.get('net_invested_value', -1), Decimal(0))
        self.assertEqual(data.get('total_buy_value', -1), Decimal(0))
        self.assertEqual(data.get('total_sell_value', -1), Decimal(0))
        self.assertEqual(data.get('fiat_liquidity', -1), Decimal(0))

    def test_overview_page_query_all_cash(self):
        # Create an portfolio
        bank_account = Account.objects.create(account_id=1,
                                            name='Bank 1',
                                            entity = 'BANK',
                                            user = self.test_user,
                                            currency = 'INR')
        demat = Account.objects.create(account_id=2,
                               name='Demat 1',
                               entity = 'DMAT',
                               user = self.test_user,
                               currency = 'INR')

        broker = Account.objects.create(account_id=3,
                               name='Broker 1',
                               entity = 'BRKR',
                               user = self.test_user,
                               currency = 'INR',
                               linked_demat_account = demat)
        # Create a portfolio
        portfolio = Portfolio.objects.create(name="Portfolio 1", 
                                             account = broker)

        # Create a market
        market = Market.objects.create(name="NSE")
        # Create a stock
        stock = Stock.objects.create(market=market,
                                     symbol = "TATASTEEL",
                                     face_value = 1,)

        # Add money to account
        Transaction.objects.create(destination_account = bank_account,
                                   transaction_type = 'CR',
                                   amount = 50000,
                                   timestamp = timezone.now())
        Transaction.objects.create(source_account = bank_account,
                                   destination_account = broker,
                                   transaction_type = 'TR',
                                   amount = 25000,
                                   timestamp = timezone.now())

        summary_url = reverse("portfolio:net-worth")
        response = self.client.get(summary_url)

        data = response.json()
        self.assertEqual(data.get('net_worth', -1), Decimal(50000))
        self.assertEqual(data.get('net_gains', -1), Decimal(0))
        self.assertEqual(data.get('net_invested_value', -1), Decimal(0))
        self.assertEqual(data.get('total_buy_value', -1), Decimal(0))
        self.assertEqual(data.get('total_sell_value', -1), Decimal(0))
        self.assertEqual(data.get('fiat_liquidity', -1), Decimal(50000))

    def test_overview_page_query_almost_investment(self):
        # Create an portfolio
        bank_account = Account.objects.create(account_id=1,
                                            name='Bank 1',
                                            entity = 'BANK',
                                            user = self.test_user,
                                            currency = 'INR')
        demat = Account.objects.create(account_id=2,
                               name='Demat 1',
                               entity = 'DMAT',
                               user = self.test_user,
                               currency = 'INR')

        broker = Account.objects.create(account_id=3,
                               name='Broker 1',
                               entity = 'BRKR',
                               user = self.test_user,
                               currency = 'INR',
                               linked_demat_account = demat)
        # Create a portfolio
        portfolio = Portfolio.objects.create(name="Portfolio 1", 
                                             account = broker)

        # Create a market
        market = Market.objects.create(name="NSE")
        # Create a stock
        stock = Stock.objects.create(market=market,
                                     symbol = "TATASTEEL",
                                     face_value = 1,)

        # Add money to account
        Transaction.objects.create(destination_account = bank_account,
                                   transaction_type = 'CR',
                                   amount = 50000,
                                   timestamp = timezone.now())
        Transaction.objects.create(source_account = bank_account,
                                   destination_account = broker,
                                   transaction_type = 'TR',
                                   amount = 50000,
                                   timestamp = timezone.now())
        
        Trade.objects.create(timestamp = timezone.now(),
                             stock = stock,
                             quantity = 1000,
                             price = 45,
                             operation = 'BUY',
                             portfolio = portfolio,
                             tax = 100.5,
                             brokerage = 200.0)

        summary_url = reverse("portfolio:net-worth")
        response = self.client.get(summary_url)

        data = response.json()
        #print(data)
        self.assertEqual(data.get('net_worth', -1), Decimal(50000 - 100.5 - 200.0))
        self.assertEqual(data.get('net_gains', -1), Decimal(0))
        self.assertEqual(data.get('net_invested_value', -1), Decimal(45000))
        self.assertEqual(data.get('total_buy_value', -1), Decimal(45000))
        self.assertEqual(data.get('total_sell_value', -1), Decimal(0))
        self.assertEqual(data.get('fiat_liquidity', -1), Decimal(5000 - 100.5 - 200.0))

        #Have some gains
        Trade.objects.create(timestamp = timezone.now(),
                             stock = stock,
                             quantity = 1000,
                             price = 50,
                             operation = 'SELL',
                             portfolio = portfolio,
                             tax = 100.5,
                             brokerage = 200.0)

        summary_url = reverse("portfolio:net-worth")
        response = self.client.get(summary_url)

        data = response.json()
        #print(data)
        self.assertEqual(data.get('net_worth', -1), Decimal(55000 - 201 - 400.0))
        self.assertEqual(data.get('net_gains', -1), Decimal(5000))
        self.assertEqual(data.get('net_invested_value', -1), Decimal(0))
        self.assertEqual(data.get('total_buy_value', -1), Decimal(45000))
        self.assertEqual(data.get('total_sell_value', -1), Decimal(50000))
        self.assertEqual(data.get('fiat_liquidity', -1), Decimal(55000 - 201 - 400.0))