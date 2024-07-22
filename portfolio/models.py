from django.db import models
from stocks.models import Stock
from django.contrib.auth.models import User

from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from datetime import datetime

# Create your models here.
class Account(models.Model):
    '''
    An account represents the place where either money or shares/assets rest.
    It can be a bank account, demat account, crypto wallet, or commodities account.

    The current value of the account is the sum of all the trades
    done across all the portfolios associated with the account, and
    the transactions done on the account.
    '''
    ENTITY_CHOICES = [
    ("BANK", "BANK"),
    ("BRKR", "BROKER"),
    ("XCNG", "EXCHANGE")
    ]
    account_id = models.BigIntegerField(verbose_name="Account ID", unique=True)
    name = models.CharField(max_length=255, blank = False, null = False)
    entity = models.CharField(choices=ENTITY_CHOICES, max_length=10)
    user = models.ForeignKey(User, null = False, blank = False, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(blank = False, default='INR', max_length=10)


class Portfolio(models.Model):
    '''
    Each account can have one or more portfolios associated with it. 
    Typically, it would be one portfolio per account, but we may get 
    fancy with long-term/short-term/FnO distinctions.

    The value of the portfolio is a normalized field computed from 
    the summation of all the historical trades on the portfolio.
    '''
    name = models.CharField(verbose_name="Portfolio name", max_length=50)
    account = models.ForeignKey(Account, null=False, blank=False, on_delete=models.CASCADE)

    def get_portfolio_value(self, date=None):
        """
        Compute the value of the portfolio at a given date.
        If no date is provided, use the current date.
        """
        if date is None:
            date = datetime.now()

        # Sum all transactions up to the given date
        transactions = Transaction.objects.filter(
            account=self.account,
            timestamp__lte=date
        ).aggregate(
            total_credits=Sum('amount', filter=models.Q(transaction="CR")),
            total_debits=Sum('amount', filter=models.Q(transaction="DB"))
        )

        # Calculate net cash in account
        net_cash = (transactions['total_credits'] or 0) - (transactions['total_debits'] or 0)

        # Sum all trades up to the given date and calculate portfolio value
        trades = Trade.objects.filter(
            portfolio=self,
            timestamp__lte=date
        )

        stock_values = trades.annotate(
            trade_value=ExpressionWrapper(
                F('quantity') * F('price'),
                output_field=DecimalField()
            )
        ).aggregate(
            total_buy=Sum('trade_value', filter=models.Q(operation='BUY')),
            total_sell=Sum('trade_value', filter=models.Q(operation='SELL'))
        )

        total_buy_value = stock_values['total_buy'] or 0
        total_sell_value = stock_values['total_sell'] or 0

        # Net portfolio value
        portfolio_value = net_cash + total_buy_value - total_sell_value
        return portfolio_value

class Trade(models.Model):
    '''
    Anything bought or sold for money is considered a trade. This effects 
    the net value of the portfolio by accounting for the assets other 
    than money in terms of money.
    Buy/Sell equity/futures/options/crypto/commodity
    '''
    TRADE_TYPE_CHOICES = [
    ("BUY", "BUY"),
    ("SELL", "SELL")
    ]
    timestamp = models.DateTimeField()
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=5)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    operation = models.CharField(choices=TRADE_TYPE_CHOICES, max_length=4)
    portfolio = models.ForeignKey(Portfolio, related_name="portfolio", null=False, blank=False, on_delete=models.CASCADE)
    tax = models.DecimalField(max_digits = 20, blank=True, decimal_places=2)
    brokerage = models.DecimalField(max_digits = 20, blank = True, decimal_places=2)

class Transaction(models.Model):
    '''
    Money coming into or going out of an account in money form (without anything for exchange)
    is a transaction. This is simply money deposited or money withdrawn from the account.
    For any demat account, the money has to first come from a bank account before we can
    conduct a trade with that money.
    '''
    TRANSACTION_TYPE_CHOICES = [
    ("CR", "CREDIT"),
    ("DB", "DEBIT")
    ]
    account = models.ForeignKey(Account, null=False, on_delete=models.CASCADE)
    transaction = models.CharField(choices=TRANSACTION_TYPE_CHOICES, max_length=6)
    amount = models.DecimalField(max_digits=20, decimal_places=3)
    timestamp = models.DateTimeField()


class Dividend(models.Model):
    '''
    A dividend is like a CREDIT operation into the account, but the 
    value is determined by the amount of the dividend stocks held on
    the record date. 
    '''
    record_date = models.DateField(null=False, blank = False)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)

    def get_total_dividend(self, portfolio, date=None):
        """
        Compute the total dividend for the portfolio up to a given date.
        If no date is provided, use the current date.
        """
        if date is None:
            date = datetime.now().date()

        # Filter trades to get quantities held on record date
        trades = Trade.objects.filter(
            portfolio=portfolio,
            stock=self.stock,
            timestamp__lte=self.record_date
        ).aggregate(
            total_quantity=Sum('quantity', filter=models.Q(operation='BUY')) -
                           Sum('quantity', filter=models.Q(operation='SELL'))
        )

        total_quantity = trades['total_quantity'] or 0
        total_dividend = total_quantity * self.amount

        return total_dividend
