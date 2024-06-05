from django.contrib.auth.models import Group, User
from rest_framework import serializers
from portfolio.models import Account, Portfolio, Trade, Transaction, Dividend
from stocks.models import Stock, Market

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'email', 'groups']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'id', 'name']

class MarketSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Market
        fields = ['url', 'id', 'name']

class StockSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Stock
        fields = ['url', 'id', 'symbol', 'face_value',
                  'market']

class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = ['url', 'id', 'account_id', 'name', 'entity',
                  'user', 'currency']

class PortfolioSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Portfolio
        fields = ['url', 'id', 'name', 'account']

class TradeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Trade
        fields = ['url', 'id', 'date', 'stock', 'quantity',
                  'price', 'operation', 'portfolio', 'tax',
                  'brokerage']
        
class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = ['url', 'id', 'account', 'transaction', 'amount',
                  'timestamp']

class DividendSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dividend
        fields = ['url', 'id', 'record_date', 'stock', 'amount']