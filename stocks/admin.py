from django.contrib import admin

from .models.company import Company
from .models.industry import Industry
from .models.listing import Listing
from .models.market import Market
from .models.stock import Stock

# Register your models here.
admin.site.register(Stock)
admin.site.register(Market)
admin.site.register(Listing)
admin.site.register(Industry)
admin.site.register(Company)