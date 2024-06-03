from django.db import models
from stocks.models import Stock
from django.contrib.auth.models import User

# Create your models here.
class Portfolio(models.Model):
    name = models.CharField(verbose_name="Portfolio name", max_length=50)
    user = models.ForeignKey(User, null=False, blank=False)

class Trade(models.Model):
    TRADE_TYPES = {"BUY": "BUY", 
                   "SELL": "SELL"}
    date = models.DateTimeField()
    stock = models.ForeignKey(Stock)
    quantity = models.DecimalField(max_digits=20)
    price = models.DecimalField(max_digits=20)
    operation = models.CharField(choices=TRADE_TYPES)
    portfolio = models.ForeignKey(Portfolio, null=False, blank=False)

