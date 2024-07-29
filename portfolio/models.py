from django.db import models
from stocks.models import Stock
from django.contrib.auth.models import User

from django.db.models import Sum, F, Q, ExpressionWrapper, DecimalField
from datetime import datetime
from django.utils import timezone

from collections import deque

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

    def get_net_account_value(self, date=None):
        """
        Compute the net value of the account at a given date.
        If no date is provided, use the current date.
        """
        if date is None:
            date = timezone.now()

        # Ensure the provided date is timezone-aware
        if timezone.is_naive(date):
            date = timezone.make_aware(date)

        # Sum all transactions up to the given date
        transactions = Transaction.objects.filter(
            account=self,
            timestamp__lte=date
        ).aggregate(
            total_credits=Sum('amount', filter=Q(transaction="CR")),
            total_debits=Sum('amount', filter=Q(transaction="DB"))
        )

        # Calculate net cash in account
        net_cash = (transactions['total_credits'] or 0) - (transactions['total_debits'] or 0)

        # Calculate total taxes and brokerage fees across all portfolios
        trades = Trade.objects.filter(
            portfolio__account=self,
            timestamp__lte=date
        ).aggregate(
            total_taxes=Sum('tax'),
            total_brokerage=Sum('brokerage')
        )

        total_taxes = trades['total_taxes'] or 0
        total_brokerage = trades['total_brokerage'] or 0

        # Calculate the value of all portfolios
        portfolio_values = sum(portfolio.get_portfolio_value(date) for portfolio in self.portfolio_set.all())

        # Net account value
        net_account_value = net_cash - total_taxes - total_brokerage + portfolio_values
        return net_account_value


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

    def get_invested_value(self, date=None):
        """
        Compute the value of the portfolio at a given date.
        If no date is provided, use the current date.
        """
        if date is None:
            date = timezone.now()

        # Ensure the provided date is timezone-aware
        if timezone.is_naive(date):
            date = timezone.make_aware(date)

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
            total_buy=Sum('trade_value', filter=Q(operation='BUY')),
            total_sell=Sum('trade_value', filter=Q(operation='SELL'))
        )

        total_buy_value = stock_values['total_buy'] or 0
        total_sell_value = stock_values['total_sell'] or 0

        # Net portfolio value
        portfolio_value = total_buy_value - total_sell_value
        return portfolio_value
    
    def get_portfolio(self, date=None):
        """
        Get the portfolio details as of a given date.
        Returns a list of tuples containing (stock, quantity, average buy price)
        for all stocks held in non-zero quantity on the requested date.
        If no date is provided, use the current date.
        """
        if date is None:
            date = timezone.now()

        # Ensure the provided date is timezone-aware
        if timezone.is_naive(date):
            date = timezone.make_aware(date)

        # Get all trades up to the given date
        trades = Trade.objects.filter(
            portfolio=self,
            timestamp__lte=date
        ).order_by('stock', 'timestamp')

        # Dictionary to hold FIFO purchase history for each stock
        stock_history = {}

        for trade in trades:
            if trade.stock not in stock_history:
                stock_history[trade.stock] = deque()

            if trade.operation == 'BUY':
                # Add to purchase history with FIFO
                stock_history[trade.stock].append((trade.quantity, trade.price))
            elif trade.operation == 'SELL':
                # Process sale according to FIFO
                quantity_to_sell = trade.quantity
                total_cost = 0
                while quantity_to_sell > 0 and stock_history[trade.stock]:
                    purchased_quantity, purchase_price = stock_history[trade.stock].popleft()
                    if purchased_quantity <= quantity_to_sell:
                        total_cost += purchased_quantity * purchase_price
                        quantity_to_sell -= purchased_quantity
                    else:
                        total_cost += quantity_to_sell * purchase_price
                        stock_history[trade.stock].appendleft((purchased_quantity - quantity_to_sell, purchase_price))
                        quantity_to_sell = 0

        # Prepare the result list
        result = []
        for stock, history in stock_history.items():
            quantity = sum(q for q, _ in history)
            if quantity > 0:
                total_cost = sum(q * p for q, p in history)
                average_buy_price = total_cost / quantity
                result.append((stock, quantity, average_buy_price))

        return result

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
    tax = models.DecimalField(max_digits = 20, blank=True, decimal_places=2, default=0)
    brokerage = models.DecimalField(max_digits = 20, blank = True, decimal_places=2, default=0)

    def __str__(self):
        return "{} {} shares of {} at {}".format(self.operation, self.quantity, self.stock.symbol, self.price)

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

    def __str__(self):
        return "Dividend {} for {} on {}".format(self.amount, self.stock.symbol, self.record_date)

    @classmethod
    def get_total_dividend(cls, portfolio, stock, date=None):
        """
        Compute the total dividend for a portfolio and stock up to a given date.
        If no date is provided, use the current date.
        """
        if date is None:
            date = timezone.now()

        # Ensure the provided date is timezone-aware
        if timezone.is_naive(date):
            date = timezone.make_aware(date)

        # Fetch all dividends for the stock
        dividends = cls.objects.filter(stock=stock, record_date__lte=date)

        total_dividend = 0

        for dividend in dividends:
            # Make record_date timezone-aware
            record_date_aware = timezone.make_aware(
                datetime.combine(dividend.record_date, datetime.min.time())
            )

            # Filter trades to get quantities held on record date
            buy_quantity = Trade.objects.filter(
                portfolio=portfolio,
                stock=stock,
                timestamp__lte=record_date_aware,
                operation='BUY'
            ).aggregate(total_buy=Sum('quantity'))['total_buy'] or 0

            sell_quantity = Trade.objects.filter(
                portfolio=portfolio,
                stock=stock,
                timestamp__lte=record_date_aware,
                operation='SELL'
            ).aggregate(total_sell=Sum('quantity'))['total_sell'] or 0

            total_quantity = buy_quantity - sell_quantity
            total_dividend += total_quantity * dividend.amount

        return total_dividend
