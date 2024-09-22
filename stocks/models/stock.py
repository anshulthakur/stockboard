from stocks.models import Market, Company
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from random import randint

class StockManager(models.Manager):
    def random(self):
        count = self.aggregate(count=models.Count('id'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]

class Stock(models.Model):
    symbol = models.CharField(blank=False,
                            null=False,
                            max_length=15)
    group = models.CharField(blank=True,
                             default='',
                             max_length=5)
    face_value = models.DecimalField(max_digits=10, decimal_places = 4)
    sid = models.BigIntegerField(default=None, 
                                 null=True,
                                 blank=True)
    market = models.ForeignKey(Market,
                             null=True,
                             to_field='name',
                             on_delete = models.CASCADE)
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.SET_NULL, blank=True)
    object_id = models.PositiveIntegerField(default=None, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    active = models.BooleanField(default=True, blank=True)

    objects = StockManager()
    def __str__(self):
        return (self.symbol)

    class Meta:
        indexes = [
            models.Index(fields=['symbol'], name='security_idx'),
            models.Index(fields=['sid'], name='sid_idx'),
            models.Index(fields=["content_type", "object_id"]),
        ]

    @classmethod
    def get_stock_symbol_by_isin(cls, isin, market):
        """
        Fetches or creates a stock using ISIN and market.
        """
        # Get the company by ISIN
        company = Company.objects.filter(isin=isin).first()
        if company:
            try:
                # Find stock associated with the company and market
                stock = cls.objects.get(
                    content_type=ContentType.objects.get_for_model(Company),
                    object_id=company.id,
                    market=market
                )
                return stock
            except cls.DoesNotExist:
                return None
        return None
    
    @classmethod
    def get_stock_symbol_by_company_name(cls, name, market):
        """
        Fetches or creates a stock using ISIN and market.
        """
        # Get the company by ISIN
        company = Company.objects.filter(name=name).first()
        if company:
            try:
                # Find stock associated with the company and market
                stock = cls.objects.get(
                    content_type=ContentType.objects.get_for_model(Company),
                    object_id=company.id,
                    market=market
                )
                return stock
            except cls.DoesNotExist:
                return None
        return None
