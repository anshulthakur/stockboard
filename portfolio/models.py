from django.db import models
from stocks.models import Stock
from django.contrib.auth.models import User

# Create your models here.
class Account(models.Model):
    '''
    An account represents the place where either money or shares/assets rest.
    It can be a bank account, demat account, crypto wallet, or commodities account.

    The current value of the account is the sum of all the trades
    done across all the portfolios associated with the account, and
    the transactions done on the account.
    '''
    ENTITIES = {"BANK": "BANK", 
                "BRKR": "BROKER",
                "XCNG": "EXCHANGE"}
    account_id = models.BigIntegerField(verbose_name="Account ID", unique=True)
    name = models.CharField(max_length=255, blank = False, null = False)
    entity = models.CharField(choices=ENTITIES, max_length=10)
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

class Trade(models.Model):
    '''
    Anything bought or sold for money is considered a trade. This effects 
    the net value of the portfolio by accounting for the assets other 
    than money in terms of money.
    Buy/Sell equity/futures/options/crypto/commodity
    '''
    TRADE_TYPES = {"BUY": "BUY", 
                   "SELL": "SELL"}
    timestamp = models.DateTimeField()
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=5)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    operation = models.CharField(choices=TRADE_TYPES, max_length=4)
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
    TRANSACTION_TYPE = {"CR": "CREDIT",
                        "DB": "DEBIT"}
    account = models.ForeignKey(Account, null=False, on_delete=models.CASCADE)
    transaction = models.CharField(choices=TRANSACTION_TYPE, max_length=6)
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
