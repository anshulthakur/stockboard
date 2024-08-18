from django.test import TestCase
from django.contrib.auth.models import User
from portfolio.models import Account, Portfolio, Trade, Transaction, Dividend
from stocks.models import Stock, Market
import datetime
from django.utils import timezone
from decimal import Decimal

class TestAccountModels(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        # Create accounts
        self.bank_account = Account.objects.create(
            account_id=1, 
            name="Bank A", 
            entity="BANK", 
            user=self.user
        )
        # Credit funds to the bank
        Transaction.objects.create(
            transaction_type="CR",
            source_account=None,
            destination_account=self.bank_account,
            amount=50000,
            timestamp=timezone.make_aware(datetime.datetime(2023, 1, 1, 0, 0, 0))
        )

        self.broker_account = Account.objects.create(
            account_id=2, 
            name="Broker A", 
            entity="BRKR", 
            user=self.user
        )
        self.demat_account = Account.objects.create(
            account_id=3, 
            name="Demat A", 
            entity="DMAT", 
            user=self.user
        )

        # Create a portfolio under the broker account
        self.portfolio = Portfolio.objects.create(
            name="My Portfolio", account=self.broker_account
        )

        # Transfer funds from bank to broker account
        Transaction.objects.create(
            transaction_type="TR",
            source_account=self.bank_account,
            destination_account=self.broker_account,
            amount=25000,
            timestamp=timezone.now()
            #timestamp=timezone.make_aware(datetime.datetime(2023, 1, 1, 0, 0, 0))
        )

        self.market = Market.objects.create(name='Test Market')
        self.stock = Stock.objects.create(
            symbol='TEST',
            group='',
            face_value=10.0,
            market=self.market
        )

        # Create a trade under the portfolio
        Trade.objects.create(
            timestamp=timezone.make_aware(datetime.datetime(2023, 1, 1, 0, 0, 0)),
            stock=self.stock,
            quantity=100,
            price=100,
            operation='BUY',
            portfolio=self.portfolio,
            tax=100,
            brokerage=50
        )
        Trade.objects.create(
            timestamp=timezone.make_aware(datetime.datetime(2023, 1, 2, 0, 0, 0)),
            stock=self.stock,
            quantity=50,
            price=110,
            operation='SELL',
            portfolio=self.portfolio,
            tax=50,
            brokerage=30
        )

    # def test_portfolio_value(self):
    #     portfolio1_value = self.portfolio1.get_invested_value(date=timezone.make_aware(datetime.datetime(2023, 1, 3, 0, 0, 0)))
    #     portfolio2_value = self.portfolio2.get_invested_value(date=timezone.make_aware(datetime.datetime(2023, 1, 3, 0, 0, 0)))

    #     expected_portfolio1_value = 10 * 100
    #     expected_portfolio2_value = -5 * 110

    #     self.assertEqual(portfolio1_value, expected_portfolio1_value)
    #     self.assertEqual(portfolio2_value, expected_portfolio2_value)

    def test_net_account_value(self):
        net_account_value = self.account.get_net_account_value(date=timezone.make_aware(datetime.datetime(2023, 1, 3, 0, 0, 0)))
        expected_portfolio1_value = 10 * 100
        expected_portfolio2_value = -5 * 110
        expected_net_cash = 2000 - 500
        expected_taxes_brokerage = 10 + 5 + 5 + 3

        expected_net_account_value = expected_net_cash - expected_taxes_brokerage + expected_portfolio1_value + expected_portfolio2_value
        self.assertEqual(net_account_value, expected_net_account_value)

    def test_get_net_account_value(self):
        # Check the net account value for the bank account (should be reduced by the transfer)
        self.assertEqual(self.bank_account.get_net_account_value(), Decimal('25000'))

        # Check the net account value for the broker account
        # Initial cash + trades - (taxes and brokerage)
        expected_value = Decimal('25000') - Decimal('100') - Decimal('50') -Decimal('10000')+ Decimal('5500') - Decimal('50') - Decimal('30')
        self.assertEqual(self.broker_account.get_net_account_value(), expected_value)

class TestPortfolioValueModels(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.account = Account.objects.create(
            account_id=123456,
            name='Test Account',
            entity='BANK',
            user=self.user,
            currency='INR'
        )
        self.portfolio = Portfolio.objects.create(
            name='Test Portfolio',
            account=self.account
        )
        self.market = Market.objects.create(name='Test Market')
        self.stock = Stock.objects.create(
            symbol='TEST',
            group='',
            face_value=10.0,
            market=self.market
        )
        self.stock2 = Stock.objects.create(
            symbol='TEST2',
            group='',
            face_value=10.0,
            market=self.market
        )

        # Add trades with taxes and brokerages
        Trade.objects.create(
            timestamp=timezone.make_aware(datetime.datetime(2023, 1, 1, 0, 0, 0)),
            stock=self.stock,
            quantity=10,
            price=100,
            operation='BUY',
            portfolio=self.portfolio,
            tax=10,
            brokerage=5
        )
        Trade.objects.create(
            timestamp=timezone.make_aware(datetime.datetime(2023, 1, 1, 0, 0, 0)),
            stock=self.stock,
            quantity=10,
            price=105,
            operation='BUY',
            portfolio=self.portfolio,
            tax=10,
            brokerage=5
        )
        Trade.objects.create(
            timestamp=timezone.make_aware(datetime.datetime(2023, 1, 2, 0, 0, 0)),
            stock=self.stock,
            quantity=5,
            price=110,
            operation='SELL',
            portfolio=self.portfolio,
            tax=5,
            brokerage=3
        )

        # Add trades for stock2
        Trade.objects.create(
            timestamp=timezone.make_aware(datetime.datetime(2023, 1, 3, 0, 0, 0)),
            stock=self.stock2,
            quantity=20,
            price=50,
            operation='BUY',
            portfolio=self.portfolio,
            tax=5,
            brokerage=2
        )


        # Add transactions
        Transaction.objects.create(
            account=self.account,
            transaction='CR',
            amount=2000,
            timestamp=timezone.make_aware(datetime.datetime(2023, 1, 1, 0, 0, 0))
        )
        Transaction.objects.create(
            account=self.account,
            transaction='DB',
            amount=500,
            timestamp=timezone.make_aware(datetime.datetime(2023, 1, 2, 0, 0, 0))
        )

    def test_portfolio_value_on_date(self):
        portfolio_value = self.portfolio.get_invested_value(date=timezone.make_aware(datetime.datetime(2023, 1, 3, 0, 0, 0)))
        expected_value = ((10 * 100)) - ((5 * 110)) + (10*105) + (50*20)
        self.assertEqual(portfolio_value, expected_value)

    def test_portfolio_value_no_transactions(self):
        new_portfolio = Portfolio.objects.create(
            name='New Portfolio',
            account=self.account
        )
        value = new_portfolio.get_invested_value()
        self.assertEqual(value, 0)

    def test_portfolio_value_no_trades(self):
        value = self.portfolio.get_invested_value(date=timezone.make_aware(timezone.datetime(2022, 12, 31, 0, 0, 0)))
        self.assertEqual(value, 0)

    def test_get_portfolio(self):
        portfolio_details = self.portfolio.get_portfolio(date=timezone.make_aware(datetime.datetime(2023, 1, 4, 0, 0, 0)))

        expected_portfolio_details = [
            (self.stock, 15, Decimal(103.33)),  # (stock, quantity, average_buy_price)
            (self.stock2, 20, 50.0)
        ]

        self.assertEqual(len(portfolio_details), len(expected_portfolio_details))
        for actual, expected in zip(portfolio_details, expected_portfolio_details):
            self.assertEqual(actual[0], expected[0])  # Check stock
            self.assertEqual(actual[1], expected[1])  # Check quantity
            self.assertAlmostEqual(actual[2], expected[2], places=2)  # Check average buy price

class TestDividendModels(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.account = Account.objects.create(
            account_id=123456,
            name='Test Account',
            entity='BANK',
            user=self.user,
            currency='INR'
        )
        self.portfolio = Portfolio.objects.create(
            name='Test Portfolio',
            account=self.account
        )
        self.market = Market.objects.create(name='Test Market')
        self.stock = Stock.objects.create(
            symbol='TEST',
            group='',
            face_value=10.0,
            market=self.market
        )

        # Create dividends
        Dividend.objects.create(
            #record_date='2023-01-01'
            record_date=datetime.date(2023, 1, 1),
            stock=self.stock,
            amount=5
        )
        Dividend.objects.create(
            record_date=datetime.date(2023, 2, 1),
            stock=self.stock,
            amount=2
        )

    def test_total_dividend(self):
        # Add trades
        Trade.objects.create(
            timestamp=timezone.make_aware(datetime.datetime(2023, 1, 1, 0, 0, 0)),
            stock=self.stock,
            quantity=10,
            price=100,
            operation='BUY',
            portfolio=self.portfolio
        )

        total_dividend = Dividend.get_total_dividend(portfolio=self.portfolio, stock=self.stock, date=timezone.make_aware(datetime.datetime(2023, 3, 1, 0, 0, 0)))
        self.assertEqual(total_dividend, (10 * 5) + (10 * 2))  # 10 stocks * 5 amount per stock + 10 stocks * 2 amount per stock

    def test_total_dividend_no_trades(self):
        # Add trades
        Trade.objects.create(
            timestamp=timezone.make_aware(datetime.datetime(2023, 1, 1, 0, 0, 0)),
            stock=self.stock,
            quantity=10,
            price=100,
            operation='BUY',
            portfolio=self.portfolio
        )
        
        new_portfolio = Portfolio.objects.create(
            name='New Portfolio',
            account=self.account
        )
        total_dividend = Dividend.get_total_dividend(portfolio=new_portfolio, stock=self.stock, date=timezone.make_aware(datetime.datetime(2023, 3, 1, 0, 0, 0)))
        self.assertEqual(total_dividend, 0)

    def test_total_dividend_no_stocks_on_record_date(self):
        # Create a trade after the record date
        Trade.objects.create(
            timestamp=timezone.make_aware(datetime.datetime(2023, 1, 2, 0, 0, 0)),
            stock=self.stock,
            quantity=10,
            price=100,
            operation='BUY',
            portfolio=self.portfolio
        )
        total_dividend = Dividend.get_total_dividend(portfolio=self.portfolio, stock=self.stock, date=timezone.make_aware(datetime.datetime(2023, 3, 1, 0, 0, 0)))
        self.assertEqual(total_dividend, 10 * 2)  # Only the second dividend counts
