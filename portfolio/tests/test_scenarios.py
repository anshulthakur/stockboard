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
class BaseTest(APITestCase):
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

    def create_account(self, entity, id, name, balance):
        self.account = Account.objects.create(
            account_id=id,
            name=name,
            entity=entity,
            user=self.user,
            currency='INR',
            balance = balance
        )

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

class TestNetworth(BaseTest):
    '''
    1. Net Worth Overview
        1.1. Fetch Net Worth Summary:
        Verify that the sum of all accounts is correctly calculated.
        Validate the distribution of wealth among different asset classes.
        Check the total number of accounts and verify consistency.
        1.2. Drilldown by Asset Class:
        Ensure correct asset distribution when filtering by asset class (e.g., cash, equities, crypto).
        1.3. Drilldown by Account Type:
        Validate the net worth distribution among different account types (e.g., bank, demat, broker).
    '''
    pass

class TestAccountDetails(BaseTest):
    '''
    2. Account Details
        2.1. Fetch Account Summary:
        Validate that the summary correctly reflects the current balance, recent transactions, and the portfolio value.
        2.2. Fetch Account Transactions:
        Ensure that transactions are correctly fetched and filtered by date, type, or amount.
        2.3. Fetch Account Portfolio:
        Verify that the portfolio is accurately displayed with the correct quantities and average buy prices.
    '''
    pass
class TestPortfolioManagement(BaseTest):
    '''
    3. Portfolio Management
        3.1. Fetch Portfolio Overview:
        Verify that the total value of the portfolio is correctly calculated based on current market prices.
        Validate the inclusion of sub-portfolios and the global portfolio view.
        3.2. Portfolio Performance Over Time:
        Ensure accurate calculation of portfolio performance metrics over different time periods (e.g., daily, monthly).
        3.3. Portfolio Asset Allocation:
        Validate the breakdown of asset allocation by category (e.g., stocks, crypto).
        3.4. Portfolio Dividends:
        Verify that dividends are correctly calculated and assigned to the respective portfolios.
    '''

class TestOrderHistory(BaseTest):
    '''
    4. Order History
        4.1. Fetch Order History:
        Verify that the order history reflects all transactions within a specified period.
        Ensure correct filtering by trade type (buy/sell), asset type, and date range.
        4.2. FIFO Calculation for Orders:
        Validate the correct application of the FIFO method for calculating stock positions and realized gains/losses.
    '''
    pass

class TestTransferStatements(BaseTest):
    '''
    5. Transfer Statement
        5.1. Fetch Transfer History:
        Ensure that all internal and external transfers are accurately fetched and listed for a specified period.
        Validate the correct identification of transfer types (inflow, outflow, internal transfer).
        5.2. Transfer Summary by Account:
        Verify the correct summary of inflows, outflows, and net transfers for each account.
    '''
    pass

class TestAssetManagement(BaseTest):
    '''
    6. Asset Management
        6.1. Fetch Asset Details:
        Ensure that individual assets are correctly displayed with their current value, purchase history, and performance metrics.
        6.2. Add New Asset:
        Verify that adding a new asset is correctly processed and reflected in the portfolio.
        6.3. Remove Asset:
        Validate the correct removal of an asset and the update of the portfolio’s value.
        6.4. Asset Price Update:
        Verify that updating the price of an asset correctly reflects on the portfolio value and performance metrics.
    '''
    pass

class TestTransactionManagement(BaseTest):
    '''
    7. Transaction Management
        7.1. Add New Transaction:
        Ensure that a new transaction (credit, debit, or transfer) is correctly added and affects the account balance.
        7.2. Update Existing Transaction:
        Validate the correct update of an existing transaction and its impact on the account/portfolio.
        7.3. Delete Transaction:
        Ensure that deleting a transaction correctly updates the account/portfolio value and historical data.
    '''
    pass

class TestInvestmentManagement(BaseTest):
    '''
    8. Investment Management
        8.1. Add New Investment:
        Verify the addition of a new investment and its correct reflection in the respective portfolio.
        8.2. Sell Investment:
        Ensure that selling an investment is accurately processed and affects the portfolio’s value.
        8.3. Fetch Investment Performance:
        Validate the correct calculation of investment performance over time, considering dividends, buy/sell prices, and other factors.
    '''
    pass

class TestReporting(BaseTest):
    '''
    9. Reporting
        9.1. Generate Account Statement:
        Ensure that account statements are correctly generated for a specified period, including all transactions and their impact.
        9.2. Generate Portfolio Performance Report:
        Verify that performance reports accurately reflect returns, asset allocation, and historical performance metrics.
        9.3. Tax Reporting:
        Validate the correct generation of tax reports, including realized gains/losses, dividends, and other taxable events.
    '''
    pass

class TestMiscellaneous(BaseTest):
    '''
    10. Miscellaneous
        10.1. User Authentication & Authorization:
        Verify that users can only access their own financial data and are correctly restricted from accessing others' data.
        10.2. Currency Conversion:
        Validate the correct conversion of values when dealing with multi-currency accounts or investments.
        10.3. Data Consistency Checks:
        Ensure that data integrity is maintained, especially during complex operations like transfers, portfolio updates, and asset price changes.
        These test cases cover a wide range of functionalities, ensuring that the financial portfolio portal is robust and reliable. You can prune or refine this list based on the specific features you prioritize in the development process.
    '''
    pass