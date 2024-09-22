from django.db import models
from stocks.models import Industry
from django.contrib.contenttypes.fields import GenericRelation

class Company(models.Model):
    name = models.CharField(blank=False, 
                            null=False,
                            max_length=255)
    isin = models.CharField(blank=False,
                            null=False,
                            max_length=15)
    # Add a GenericRelation to Stock for reverse lookup
    stocks = GenericRelation('Stock', content_type_field='content_type', object_id_field='object_id')

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='company_idx'),
            models.Index(fields=['isin'], name='isin_idx'),
        ]

    @classmethod
    def get_or_create_company_by_isin(cls, isin):
        """
        Fetches or creates a company using ISIN.
        """
        try:
            company = cls.objects.get(isin=isin)
        except cls.DoesNotExist:
            # External API call to fetch company details by ISIN
            # You can replace this block with your API logic
            #company_data = external_api_fetch_company_by_isin(isin)  
            company_data = {'name': 'TODO'} #TODO
            company = cls.objects.create(name=company_data['name'], isin=isin)
        return company