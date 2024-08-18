from django.contrib import admin

from .models import (Account, Portfolio, Trade, Transaction, Dividend)

admin.site.register(Account)
admin.site.register(Portfolio)
admin.site.register(Trade)
admin.site.register(Transaction)
admin.site.register(Dividend)