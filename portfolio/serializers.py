from django.contrib.auth.models import Group, User
from rest_framework import serializers
from portfolio.models import Account, Portfolio, Trade, Transaction, Dividend
from stocks.models import Stock, Market

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'email', 'groups']
        extra_kwargs = {
            'url': {'view_name': 'portfolio:user-detail',}
        }

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'id', 'name']
        extra_kwargs = {
            'url': {'view_name': 'portfolio:group-detail',}
        }

class MarketSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Market
        fields = ['url', 'id', 'name']
        extra_kwargs = {
            'url': {'view_name': 'portfolio:market-detail',}
        }

class StockSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Stock
        fields = ['url', 'id', 'symbol', 'face_value',
                  'market']
        extra_kwargs = {
            'url': {'view_name': 'portfolio:stock-detail',}
        }

class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = ['url', 'id', 'account_id', 'name', 'entity',
                  'user', 'currency']
        extra_kwargs = {
            'url': {'view_name': 'portfolio:account-detail',},
            'user': {'view_name': 'portfolio:user-detail',},
        }

class PortfolioSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Portfolio
        fields = ['url', 'id', 'name', 'account']
        extra_kwargs = {
            'url': {'view_name': 'portfolio:portfolio-detail',},
            'account': {'view_name': 'portfolio:account-detail',},
        }

class TradeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Trade
        fields = ['url', 'id', 'timestamp', 'stock', 'quantity',
                  'price', 'operation', 'portfolio', 'tax',
                  'brokerage']
        extra_kwargs = {
            'url': {'view_name': 'portfolio:trade-detail',},
            'portfolio': {'view_name': 'portfolio:portfolio-detail',},
            'stock': {'view_name': 'portfolio:stock-detail',},
        }
        
class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = ['url', 'id', 'account', 'transaction', 'amount',
                  'timestamp']
        extra_kwargs = {
            'url': {'view_name': 'portfolio:transaction-detail',},
            'account': {'view_name': 'portfolio:account-detail',},
        }

class DividendSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dividend
        fields = ['url', 'id', 'record_date', 'stock', 'amount']
        extra_kwargs = {
            'url': {'view_name': 'portfolio:dividend-detail',},
            'stock': {'view_name': 'portfolio:stock-detail',}
        }