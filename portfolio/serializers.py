from django.contrib.auth.models import Group, User
from django.db.models import Q
from rest_framework import serializers
from portfolio.models import Account, Portfolio, Trade, Transaction, Dividend
from stocks.models import Stock, Market
from decimal import Decimal
from datetime import datetime
from django.utils import timezone
from collections import defaultdict
import json

SPLITS_FILE = '/home/anshul/web/stockboard/stock_splits.json'
BONUSES_FILE = '/home/anshul/web/stockboard/stock_bonuses.json'

splits_object = None
bonuses_object = None 

def get_splits_object():
    global splits_object

    if splits_object is None:
        with open(SPLITS_FILE, 'r') as f:
            splits_object = json.load(f)
            splits_object = sorted(splits_object, key=lambda x: datetime.strptime(x['ex-date'], "%d %B %Y"))
    return splits_object

def get_bonuses_object():
    global bonuses_object

    if bonuses_object is None:
        with open(BONUSES_FILE, 'r') as f:
            bonuses_object = json.load(f)
            bonuses_object = sorted(bonuses_object, key=lambda x: datetime.strptime(x['ex-date'], "%d %B %Y"))
    return bonuses_object

def get_split_bonus_data(stock):
        """
        Fetch the stock split/bonus data from a JSON file (or another source).
        """
        split_data = get_splits_object()
        # Return all matching entries for the stock
        s_data = [entry for entry in split_data if \
                ((entry['nse'] and entry['nse'].strip().upper() == stock.symbol) \
                 or (entry['bse'] and entry['bse'].strip().upper() == stock.sid))]
        
        bonus_data = get_bonuses_object()
        b_data = [entry for entry in bonus_data if \
                ((entry['nse'] and entry['nse'].strip().upper() == stock.symbol) \
                 or (entry['bse'] and entry['bse'].strip().upper() == stock.sid))]
        
        return [s_data, b_data]

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
            'cash_balance': {'read_only': True},  # Marking cash_balance as read-only
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
        return obj.get_realized_gains()


class HoldingSerializer(serializers.Serializer):
    stock = serializers.CharField(read_only=True, required=False)
    symbol = serializers.CharField(read_only=True, required=False)
    shares = serializers.DecimalField(max_digits=20, decimal_places=2,
                                      read_only=True, required=False)
    price = serializers.DecimalField(max_digits=20, decimal_places=2,
                                     read_only=True, required=False)
    cost = serializers.DecimalField(max_digits=20, decimal_places=2,
                                    read_only=True, required=False)
    cmp = serializers.DecimalField(max_digits=20, decimal_places=2,
                                   read_only=True, required=False)
    value = serializers.DecimalField(max_digits=20, decimal_places=2,
                                     read_only=True, required=False)
    pnl = serializers.DecimalField(max_digits=20, decimal_places=2,
                                   read_only=True, required=False)
    day_change = serializers.DecimalField(max_digits=20, decimal_places=2,
                                          read_only=True, required=False)

    class Meta:
        model = None


class TradeSerializer(serializers.HyperlinkedModelSerializer):
    symbol = serializers.CharField(read_only=True, required=False)
    market = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = Trade
        fields = ['url', 'id', 'timestamp', 'stock', 'quantity',
                  'price', 'operation', 'portfolio', 'tax',
                  'brokerage', 'trade_id', 'symbol', 'market']
        extra_kwargs = {
            'url': {'view_name': 'portfolio:trade-detail',},
            'portfolio': {'view_name': 'portfolio:portfolio-detail',},
            'stock': {'view_name': 'portfolio:stock-detail',},
            'symbol': {'required': False,},
            'market': {'required': False,},
        }
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)  # Call the parent method
        representation['symbol'] = instance.stock.symbol
        representation['market'] = instance.stock.market.name if instance.stock.market else ''
        return representation  # Return the modified representation

class BulkTradeUnit(serializers.HyperlinkedModelSerializer):
    stock_symbol = serializers.CharField(write_only=True, required=False)
    isin = serializers.CharField(write_only=True, required=False)
    exchange = serializers.CharField(write_only=True, required=True)
    name = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Trade
        fields = ['timestamp', 'quantity', 'price', 
                  'operation', 'portfolio', 'tax', 'brokerage', 'trade_id', 
                  'stock_symbol', 'isin', 'exchange', 'name']
        extra_kwargs = {
            'portfolio': {'view_name': 'portfolio:portfolio-detail',},
        }

    def validate(self, data):
        stock_symbol = data.get('stock_symbol').strip().upper() if 'stock_symbol' in data else None
        isin = data.get('isin').strip().upper() if 'isin' in data else None
        name = data.get('name', '').strip().upper() if 'name' in data else None

        market_name = data.get('exchange').upper()

        if not stock_symbol and not isin:
            raise serializers.ValidationError("Either ISIN or Stock Symbol must be provided.")
        
        # Fetch or create the stock based on ISIN or stock symbol
        market = Market.objects.filter(name=market_name).first()
        if not market:
            market = Market.objects.create(name=market_name)

        stock = None
        if isin:
            stock = Stock.get_stock_symbol_by_isin(isin, market)
            data['stock'] = stock
            if stock == None and stock_symbol is None and name is None:
                raise serializers.ValidationError(f"Could not find a stock with isin '{isin}'.")
        if stock == None and stock_symbol:
            stock = Stock.objects.filter(symbol=stock_symbol, market=market).first()
            if stock == None and name is None:
                raise serializers.ValidationError(f"Could not find a stock with symbol '{stock_symbol}'.")
            data['stock'] = stock
        if stock == None and name:
            stock = Stock.get_stock_symbol_by_company_name(name, market)
            data['stock'] = stock
            if stock == None:
                raise serializers.ValidationError(f"Could not find a stock with name '{name}'.")
        return data

class BulkTradeSerializer(serializers.ListSerializer):
    child = BulkTradeUnit()

    def create(self, validated_data):
        trade_ids = []
        trades_to_create = []
        duplicates_to_update = []
        reconciliation_trades = {}  # Keep track of cumulative adjustments per stock

        # Step 1: Organize trades per stock
        trades_by_stock = defaultdict(list)

        # Populate trades_by_stock dictionary with trades, assuming 'validated_data' contains trades
        for item in validated_data:
            item.pop('stock_symbol', None)
            item.pop('isin', None)
            item.pop('exchange', None)
            item.pop('name', None)
            
            stock = item.get('stock')  # Assuming 'stock' holds the stock object
            trade_date = item.get('timestamp').date()
            trades_by_stock[stock.symbol].append(item)

        # Sort trades per stock by date
        for stock_symbol in trades_by_stock:
            trades_by_stock[stock_symbol].sort(key=lambda x: x['timestamp'])

        # Step 2: Load and sort stock split/bonus data
        split_bonus_events = defaultdict(list)

        for stock_symbol, trades in trades_by_stock.items():
            stock = trades[0].get('stock')  # Assuming all trades have the same stock
            split_data, bonus_data = get_split_bonus_data(stock)
            
            for split in split_data:
                ex_date = datetime.strptime(split['ex-date'], '%d %B %Y')
                split_bonus_events[stock_symbol].append({
                    'type': 'split',
                    'ex_date': ex_date,
                    'old_face_value': float(split['old-face-value']),
                    'new_face_value': float(split['new-face-value']),
                })

            for bonus in bonus_data:
                ex_date = datetime.strptime(bonus['ex-date'], '%d %B %Y')
                ratio = bonus['ratio'].split(':')
                bonus_factor = (float(ratio[0]) / float(ratio[1]))
                split_bonus_events[stock_symbol].append({
                    'type': 'bonus',
                    'ex_date': ex_date,
                    'factor': bonus_factor,
                })
        # Sort events for each stock by date
        for stock_symbol in split_bonus_events:
            split_bonus_events[stock_symbol].sort(key=lambda x: x['ex_date'])

        # Step 3: Compute reconciliation trades
        for stock_symbol, events in split_bonus_events.items():
            reconciliation = {
                'buy_qty': 0,
                'sell_qty': 0,
                'portfolio': trades_by_stock[stock_symbol][0]['portfolio'],
                'ex_date': None  # To track each event's ex-date
            }
            
            trades = trades_by_stock[stock_symbol]
            
            for event in events:
                for trade in trades:
                    trade_date = trade.get('timestamp').date()
                    
                    if trade_date < event['ex_date'].date():
                        if event['type'] == 'split':
                            factor = event['old_face_value'] / event['new_face_value']
                            if trade['operation'] == 'BUY':
                                reconciliation['buy_qty'] += int(trade['quantity'] * Decimal(factor - 1))
                            elif trade['operation'] == 'SELL':
                                reconciliation['sell_qty'] += int(trade['quantity'] * Decimal(factor - 1))
                        elif event['type'] == 'bonus':
                            if trade['operation'] == 'BUY':
                                reconciliation['buy_qty'] += int(float(trade['quantity']) * event['factor'])
                            elif trade['operation'] == 'SELL':
                                reconciliation['sell_qty'] += int(float(trade['quantity']) * event['factor'])
                
                # Create a single reconciliation trade for the current event
                cumulative_buy = reconciliation['buy_qty']
                cumulative_sell = reconciliation['sell_qty']
                
                if cumulative_buy > 0 or cumulative_sell > 0:
                    reconciliation_trade = {
                        'stock':trades[0]['stock'],
                        'timestamp':timezone.make_aware(event['ex_date']),
                        'operation':'BUY',
                        'quantity':cumulative_buy - cumulative_sell,
                        'price':0,  # Zero-cost
                        'trade_id':f"RECON-{stock_symbol}-{event['ex_date']}",
                        'portfolio':reconciliation['portfolio']
                    }
                    #print('create', reconciliation_trade)
                    trades.append(reconciliation_trade)  # Insert the reconciliation trade

                # Reset reconciliation after each event
                reconciliation['buy_qty'] = 0
                reconciliation['sell_qty'] = 0

            # Sort trades again after inserting reconciliation trades
            trades.sort(key=lambda x: x['timestamp'])

        # Step 4: Save all trades to DB
        trades_to_create = []
        duplicates_to_update = []

        for stock_symbol, trades in trades_by_stock.items():
            for trade in trades:
                existing_trade = Trade.objects.filter(trade_id=trade['trade_id']).first()
                if existing_trade:
                    for key, value in trade.items():
                        setattr(existing_trade, key, value)
                    duplicates_to_update.append(existing_trade)
                else:
                    trades_to_create.append(Trade(**trade))

        # Create new trades
        #Can't do a bulk_create because we have dependencies to resolve
        #Trade.objects.bulk_create(trades_to_create)
        for trade in trades_to_create:
            #print(trade)
            trade.save()

        # Update existing trades (duplicates)
        for trade in duplicates_to_update:
            trade.save()

        return trades_to_create + duplicates_to_update #+ reconciliation_trades


    def calculate_reconciliation_quantity(self, buy_quantity, sell_quantity, old_face_value, new_face_value):
        """
        Calculate the net reconciliation quantity after a stock split or bonus.
        """
        net_quantity = buy_quantity - sell_quantity
        old_face_value = float(old_face_value)
        new_face_value = float(new_face_value)

        # Calculate the additional shares due to the split or bonus
        additional_quantity = int(net_quantity * (old_face_value / new_face_value)) - net_quantity
        return additional_quantity

    def create_reconciliation_trades(self, stock_reconciliations, stock_splits_data):
        """
        Create reconciliation trades for each stock based on split/bonus info.
        """
        reconciliation_trades = []

        for stock_id, data in stock_reconciliations.items():
            buy_quantity = data['buy']
            sell_quantity = data['sell']
            ex_date = data['ex_date']

            # Get the stock split/bonus info
            stock_split_info = stock_splits_data[stock_id]
            old_face_value = stock_split_info['old-face-value']
            new_face_value = stock_split_info['new-face-value']

            # Calculate the reconciliation quantity (net shares to be credited at zero cost)
            reconciliation_quantity = self.calculate_reconciliation_quantity(
                buy_quantity, sell_quantity, old_face_value, new_face_value
            )

            if reconciliation_quantity > 0:
                # Create the reconciliation trade (credit additional shares at zero cost)
                reconciliation_trade = Trade(
                    trade_id=f"reconciliation_{stock_id}_{ex_date}",
                    portfolio=None,  # Or assign the correct portfolio
                    stock_id=stock_id,
                    quantity=reconciliation_quantity,
                    price=0,
                    brokerage=0,
                    tax=0,
                    timestamp=ex_date,
                    operation='BUY'  # Adding shares due to the split/bonus
                )
                reconciliation_trades.append(reconciliation_trade)

        return reconciliation_trades

        
class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = ['url', 'id', 'source_account', 'destination_account',
                  'transaction_type', 'asset_type', 'amount',
                  'timestamp', 'notes', 'transaction_id']
        extra_kwargs = {
            'url': {'view_name': 'portfolio:transaction-detail',},
            'source_account': {'view_name': 'portfolio:account-detail',},
            'destination_account': {'view_name': 'portfolio:account-detail',},
            'asset_type': {'required': False},
        }
    
    def create(self, validated_data):
        if 'asset_type' not in validated_data:
            validated_data['asset_type'] = 'CASH'
        return super().create(validated_data)

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
        net_gains = sum(account.get_realized_gains() for account in accounts)
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