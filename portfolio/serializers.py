from django.contrib.auth.models import Group, User
from django.db.models import Q
from rest_framework import serializers
from portfolio.models import Account, Portfolio, Trade, Transaction, Dividend
from stocks.models import Stock, Market
from decimal import Decimal
from datetime import datetime
from django.utils import timezone
import json

SPLITS_FILE = '/home/anshul/stockboard/stock_splits.json'
BONUSES_FILE = '/home/anshul/stockboard/stock_bonuses.json'

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

        for item in validated_data:
            is_duplicate = False 
            item.pop('stock_symbol', None)
            item.pop('isin', None)
            item.pop('exchange', None)
            item.pop('name', None)
            trade_id = item['trade_id']
            trade_ids.append(trade_id)

            # Check if trade already exists
            existing_trade = Trade.objects.filter(trade_id=trade_id).first()
            if existing_trade:
                # Update existing trade (duplicates)
                for key, value in item.items():
                    setattr(existing_trade, key, value)
                duplicates_to_update.append(existing_trade)
                is_duplicate = True
            else:
                trades_to_create.append(Trade(**item))
            
            if not is_duplicate:  # Handle bonus/splits
                stock = item.get('stock')  # Assuming 'stock' holds the stock object
                trade_date = item.get('timestamp').date()

                # Fetch the stock's split/bonus history
                split_data, bonus_data = get_split_bonus_data(stock)

                # if len(split_data) > 0 or len(bonus_data) > 0:
                #     print(item)
                #     print(split_data)
                #     print(bonus_data)
                if len(split_data) == 0 and len(bonus_data) == 0:
                    continue
                stock_identifier = None
                if stock.symbol:
                    stock_identifier = stock.symbol  # NSE symbol as string
                elif stock.sid:
                    stock_identifier = str(stock.sid)  # BSE ID converted to string for uniformity

                if stock_identifier not in reconciliation_trades:
                    reconciliation_trades[stock_identifier] = {
                        'buy_qty': 0,
                        'sell_qty': 0,
                        'portfolio': item.get('portfolio'),
                        'ex_date': None  # Track ex-date from splits and bonuses
                    }
                current_trade = {
                        'buy_qty': 0,
                        'sell_qty': 0,
                        'portfolio': item.get('portfolio'),
                        'ex_date': None  # Track ex-date from splits and bonuses
                    }

                # Apply stock splits first
                for split in split_data:
                    ex_date = datetime.strptime(split['ex-date'], '%d %B %Y')

                    if trade_date < ex_date.date():
                        #print('Adjust for split', split)
                        # Calculate cumulative quantity and zero-cost trades to be reconciled
                        old_face_value = float(split['old-face-value'])
                        new_face_value = float(split['new-face-value'])
                        factor = (old_face_value / new_face_value)
                        current_trade['ex_date'] = ex_date  # Update ex-date

                        # Add adjustments for buys and sells before ex-date
                        if item['operation'] == 'BUY':
                            current_trade['buy_qty'] += int(item['quantity'] * Decimal(factor - 1))
                            #print(f'Add buy {int(item['quantity'] * Decimal(factor - 1))} for {stock_identifier}')
                        elif item['operation'] == 'SELL':
                            current_trade['sell_qty'] += int(item['quantity'] * Decimal(factor - 1))
                            #print(f'Add sell {int(item['quantity'] * Decimal(factor - 1))} for {stock_identifier}')

                # Apply stock bonuses to the adjusted quantities after the split
                for bonus in bonus_data:
                    #print(bonus)
                    ex_date = datetime.strptime(bonus['ex-date'], '%d %B %Y')

                    if trade_date < ex_date.date():
                        # Calculate cumulative quantity and zero-cost trades to be reconciled
                        ratio = bonus['ratio'].split(':')
                        bonus_factor = (float(ratio[0]) / float(ratio[1]))
                        #print(f'Adjust for bonus factor {bonus_factor}', bonus)
                        current_trade['ex_date'] = ex_date  # Update ex-date

                        # Apply bonus to already adjusted quantities due to splits
                        adjusted_buy_qty = current_trade['buy_qty'] + item['quantity']
                        adjusted_sell_qty = current_trade['sell_qty'] + item['quantity']

                        if item['operation'] == 'BUY':
                            current_trade['buy_qty'] += Decimal(int(float(adjusted_buy_qty) * bonus_factor))
                            #print(f'Add buy {Decimal(int(float(adjusted_buy_qty) * bonus_factor))} for {stock_identifier}')
                        elif item['operation'] == 'SELL':
                            current_trade['sell_qty'] += Decimal(int(float(adjusted_sell_qty) * bonus_factor))
                            #print(f'Add sell {Decimal(int(float(adjusted_sell_qty) * bonus_factor))} for {stock_identifier}')
                
                reconciliation_trades[stock_identifier]['buy_qty'] += current_trade['buy_qty']
                reconciliation_trades[stock_identifier]['sell_qty'] += current_trade['sell_qty']
                reconciliation_trades[stock_identifier]['ex_date'] = current_trade['ex_date']


        # Create reconciliation trades for stocks after split/bonus
        for stock_identifier, reconciliation in reconciliation_trades.items():
            cumulative_buy = Decimal(reconciliation['buy_qty'] - reconciliation['sell_qty'])
            print(stock, reconciliation)
            if cumulative_buy > 0:
                # Add zero-cost reconciliation trade
                try:
                    stock_obj = Stock.objects.filter(Q(sid=stock_identifier)).first()
                except:
                    stock_obj = Stock.objects.filter(Q(symbol=stock_identifier)).first()
                
                # Handle BSE ID specifically as an integer match
                if not stock_obj:
                    stock_obj = Stock.objects.filter(sid=int(stock_identifier)).first()

                if stock_obj:
                    reconciliation_trade = Trade(
                        stock=stock_obj,
                        timestamp=timezone.make_aware(reconciliation['ex_date']),
                        operation='BUY',
                        quantity=cumulative_buy,
                        price=0,  # Zero-cost
                        trade_id=f"RECON-{stock_identifier}-{reconciliation['ex_date']}",
                        portfolio = reconciliation['portfolio']
                    )
                    print('create', reconciliation_trade)
                    trades_to_create.append(reconciliation_trade)

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