from django.contrib.auth.models import Group, User
from rest_framework import serializers
from portfolio.models import Account, Portfolio, Trade, Transaction, Dividend
from stocks.models import Stock, Market
from decimal import Decimal

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
    net_account_value = serializers.SerializerMethodField()
    class Meta:
        model = Account
        fields = ['url', 'id', 'account_id', 'name', 'entity',
                  'user', 'currency', 'cash_balance', 'parent_account',
                  'linked_demat_account', 'net_account_value']
        extra_kwargs = {
            'url': {'view_name': 'portfolio:account-detail',},
            'user': {'view_name': 'portfolio:user-detail', 'required': False},
            'linked_demat_account': {'view_name': 'portfolio:account-detail',},
            'parent_account': {'view_name': 'portfolio:account-detail',},
            'cash_balance': {'required': False},  # Marking cash_balance as optional
        }
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        else:
            raise serializers.ValidationError("User is required.")
        return super().create(validated_data)

    def get_net_account_value(self, obj):
        return obj.get_net_account_value()
    
class PortfolioSerializer(serializers.HyperlinkedModelSerializer):
    invested_value = serializers.SerializerMethodField()
    current_value = serializers.SerializerMethodField()
    realized_profit = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = ['url', 'id', 'name', 'account', 'invested_value', 'current_value',
                  'realized_profit']
        extra_kwargs = {
            'url': {'view_name': 'portfolio:portfolio-detail',},
            'account': {'view_name': 'portfolio:account-detail',},
        }

    def get_invested_value(self, obj):
        return obj.get_invested_value()
    
    def get_current_value(self, obj):
        return obj.get_portfolio_value()

    def get_realized_profit(self, obj):
        return obj.get_net_gains()

class BulkTradeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Trade
        fields = ['url', 'id', 'timestamp', 'stock', 'quantity',
                  'price', 'operation', 'portfolio', 'tax',
                  'brokerage', 'trade_id']
        extra_kwargs = {
            'url': {'view_name': 'portfolio:trade-detail', 'lookup_field': 'id'},
            'stock': {'view_name': 'portfolio:stock-detail', 'lookup_field': 'id'},
            'portfolio': {'view_name': 'portfolio:portfolio-detail', 'lookup_field': 'id'}
        }

    def create(self, validated_data):
        trade_ids = [item['id'] for item in validated_data]
        existing_trades = Trade.objects.filter(id__in=trade_ids).values_list('id', flat=True)
        new_trades = [Trade(**item) for item in validated_data if item['id'] not in existing_trades]
        Trade.objects.bulk_create(new_trades)
        return new_trades

class TradeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Trade
        fields = ['url', 'id', 'timestamp', 'stock', 'quantity',
                  'price', 'operation', 'portfolio', 'tax',
                  'brokerage', 'trade_id']
        extra_kwargs = {
            'url': {'view_name': 'portfolio:trade-detail',},
            'portfolio': {'view_name': 'portfolio:portfolio-detail',},
            'stock': {'view_name': 'portfolio:stock-detail',},
        }
        
class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = ['url', 'id', 'source_account', 'destination_account',
                  'transaction_type', 'amount',
                  'timestamp', 'notes', 'transaction_id']
        extra_kwargs = {
            'url': {'view_name': 'portfolio:transaction-detail',},
            'source_account': {'view_name': 'portfolio:account-detail',},
            'destination_account': {'view_name': 'portfolio:account-detail',},
        }

class DividendSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dividend
        fields = ['url', 'id', 'record_date', 'stock', 'amount']
        extra_kwargs = {
            'url': {'view_name': 'portfolio:dividend-detail',},
            'stock': {'view_name': 'portfolio:stock-detail',}
        }

class UserFinancialOverviewSerializer(serializers.Serializer):
    net_worth = serializers.DecimalField(max_digits=20, decimal_places=2)
    net_gains = serializers.DecimalField(max_digits=20, decimal_places=2)
    net_invested_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_buy_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_sell_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    fiat_liquidity = serializers.DecimalField(max_digits=20, decimal_places=2)

    def to_representation(self, instance):
        user = self.context['request'].user
        accounts = Account.objects.filter(user=user)
        
        buy_sell_data = {
            'buy_trades': Decimal(0.0),
            'sell_trades': Decimal(0.0),
            'gains': Decimal(0.0)
        }
        for account in accounts:
            b_s_data = account.get_net_gains()
            buy_sell_data['buy_trades'] += b_s_data['buy_trades']
            buy_sell_data['sell_trades'] += b_s_data['sell_trades']
            buy_sell_data['gains'] += b_s_data['gains']
        
        net_worth = sum(account.get_net_account_value() for account in accounts)
        net_invested_value = sum(account.get_net_invested_value() for account in accounts)
        net_gains = buy_sell_data['gains']
        total_buy_value = buy_sell_data['buy_trades']
        total_sell_value = buy_sell_data['sell_trades']
        fiat_liquidity = sum(account.cash_balance for account in accounts if account.entity not in ['DPST'])

        return {
            'net_worth': net_worth,
            'net_gains': net_gains,
            'net_invested_value': net_invested_value,
            'total_buy_value': total_buy_value,
            'total_sell_value': total_sell_value,
            'fiat_liquidity': fiat_liquidity,
        }