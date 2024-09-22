from django.db import models
from stocks.models import Stock
from django.contrib.auth.models import User

from django.db.models import Sum, F, Q, Case, When, ExpressionWrapper, DecimalField
from datetime import datetime
from django.utils import timezone
from decimal import Decimal
from collections import deque
from django.core.exceptions import ValidationError

class Account(models.Model):
    """
    Represents a financial account where funds or assets are held.
    Accounts can be categorized based on their type (e.g., Bank, Broker, Exchange).
    """
    ENTITY_CHOICES = [
        ("BANK", "Bank Account"),
        ("DPST", "Deposit Account"),
        ("BRKR", "Brokerage Account"),
        ("XCNG", "Exchange Account"),
        ("DMAT", "Demat Account"),
        ("CMDT", "Commodity Account"),
        ("CRYP", "Crypto Account"),
        ("SUB", "Virtual Account"),
        ("LOCK", "Locker"),
    ]
    
    account_id = models.BigIntegerField(verbose_name="Account ID", unique=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    entity = models.CharField(choices=ENTITY_CHOICES, max_length=10)
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(blank=False, default='INR', max_length=10)
    #We don't want cash_balance to be directly settable
    _cash_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True, db_column='cash_balance')  # Tracks cash balance
    parent_account = models.ForeignKey('self', on_delete=models.CASCADE, 
                                       null=True, blank=True,
                                       related_name='sub_accounts')
    linked_demat_account = models.OneToOneField(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='linked_broker_account'
    )

    class Meta:
        indexes = [
            models.Index(fields=['account_id']),
        ]
    
    @property
    def cash_balance(self):
        return self._cash_balance

    @cash_balance.setter
    def cash_balance(self, value):
        self._cash_balance = value

    def __init__(self, *args, **kwargs):
        if 'cash_balance' in kwargs:
            kwargs.pop('cash_balance')
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.entity}"

    def update_cash_balance(self, amount):
        """
        Updates the cash balance in the account.
        """
        self.cash_balance += amount
        self.save()

    def get_net_account_value(self, date=None):
        """
        Compute the net value of the account at a given date.
        If no date is provided, use the current date.
        """
        if date is None:
            date = timezone.now()

        # Ensure the provided date is timezone-aware
        if timezone.is_naive(date):
            date = timezone.make_aware(date)

        # Get this account and its sub-accounts
        accounts = [self] + list(self.sub_accounts.all())
        # Sum all transactions up to the given date for credits and debits, including transfers (only for cash)
        transactions = Transaction.objects.filter(
            timestamp__lte=date,
            asset_type='CASH'
        ).filter(
            Q(source_account__in=accounts) | Q(destination_account__in=accounts)
        ).aggregate(
            total_credits=Sum('amount', filter=Q(transaction_type="CR") | Q(transaction_type="TR", destination_account__in=accounts)),
            total_debits=Sum('amount', filter=Q(transaction_type="DB") | Q(transaction_type="TR", source_account__in=accounts))
        )

        # Calculate net cash in account
        net_cash = (transactions['total_credits'] or 0) - (transactions['total_debits'] or 0)

        # Calculate the value of all portfolios
        portfolio_values = sum(portfolio.get_portfolio_value(date) for portfolio in self.portfolio_set.all())
        # print(self)
        # print(f"Credits: {transactions['total_credits']}")
        # print(f"Debits: {transactions['total_debits']}")
        # print(f"Net cash: {net_cash}")
        # print(f"Taxes: {total_taxes}")
        # print(f"Brokerage: {total_brokerage}")
        # print(f"Portfolio: {portfolio_values}")

        # Net account value
        net_account_value = net_cash + portfolio_values #- total_taxes - total_brokerage 
        return net_account_value
    
    def get_net_invested_value(self, date=None):
        if date is None:
            date = timezone.now()

        # Ensure the provided date is timezone-aware
        if timezone.is_naive(date):
            date = timezone.make_aware(date)
        
        portfolio_values = sum(portfolio.get_invested_value(date) for portfolio in self.portfolio_set.all())

        return portfolio_values
    
    def get_net_portfolio_value(self, date=None):
        if date is None:
            date = timezone.now()

        # Ensure the provided date is timezone-aware
        if timezone.is_naive(date):
            date = timezone.make_aware(date)
        
        portfolio_values = sum(portfolio.get_portfolio_value(date) for portfolio in self.portfolio_set.all())

        return portfolio_values
    
    def get_net_gains(self, date=None):
        if date is None:
            date = timezone.now()

        # Ensure the provided date is timezone-aware
        if timezone.is_naive(date):
            date = timezone.make_aware(date)
        
        buy_sell_data = {
            'buy_trades': Decimal(0.0),
            'sell_trades': Decimal(0.0)
        }
        for portfolio in self.portfolio_set.all():
            b_s_data = portfolio.get_net_gains(date)
            buy_sell_data['buy_trades'] += b_s_data['buy_trades']
            buy_sell_data['sell_trades'] += b_s_data['sell_trades']
        
        buy_sell_data['gains'] = buy_sell_data['sell_trades'] - buy_sell_data['buy_trades']
        return buy_sell_data
    
    def get_realized_gains(self, date=None):
        if date is None:
            date = timezone.now()

        # Ensure the provided date is timezone-aware
        if timezone.is_naive(date):
            date = timezone.make_aware(date)
        gains = 0
        for portfolio in self.portfolio_set.all():
            gains += portfolio.get_realized_gains()
        #print(f'{self.name}: Gains: {gains}')
        return gains

    def get_net_taxes_and_brokerages(self, date=None):
        """
        Compute the net taxes and brokerages paid until a given date.
        If no date is provided, use the current date.
        """
        if date is None:
            date = timezone.now()

        # Ensure the provided date is timezone-aware
        if timezone.is_naive(date):
            date = timezone.make_aware(date)

        # Get this account and its sub-accounts
        accounts = [self] + list(self.sub_accounts.all())

        # Calculate total taxes and brokerage fees across all portfolios
        trades = Trade.objects.filter(
            portfolio__account__in=accounts,
            timestamp__lte=date
        ).aggregate(
            total_taxes=Sum('tax'),
            total_brokerage=Sum('brokerage')
        )

        total_taxes = trades['total_taxes'] or 0
        total_brokerage = trades['total_brokerage'] or 0

        return {'taxes': total_taxes, 'brokerage': total_brokerage}
    
class GlobalPortfolio(models.Model):
    """
    Represents a global view of multiple portfolios, providing a consolidated view.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=False, null=False)
    portfolios = models.ManyToManyField('Portfolio', related_name="global_portfolios")

    def __str__(self):
        return f"Global Portfolio: {self.name}"

    def get_global_value(self, date=None):
        """
        Calculates the overall value of the global portfolio across all linked portfolios.
        """
        total_value = sum(portfolio.get_invested_value(date) for portfolio in self.portfolios.all())
        return total_value


class Portfolio(models.Model):
    """
    Represents a portfolio within an account, possibly part of a larger portfolio structure.
    """
    name = models.CharField(max_length=50)
    account = models.ForeignKey(Account, null=False, blank=False, on_delete=models.CASCADE)
    parent_portfolio = models.ForeignKey('self', null=True, blank=True, related_name='sub_portfolios', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} in {self.account.name}"
    
    def save(self, *args, **kwargs):
        # Ensure that the portfolio is only associated with a brokerage account or an appropriate account type
        if self.account.entity not in ["BRKR", "DMAT", "CMDT", "CRYP"]:
            raise ValidationError("Portfolio can only be associated with a Broker, Demat, Commodity, or Crypto account.")
        
        # Call the original save method
        super().save(*args, **kwargs)

    def calculate_own_value(self, date=None):
        # Calculate this portfolio's value excluding sub-portfolios
        """
        Get the portfolio details as of a given date.
        Returns a list of tuples containing (stock, quantity, average buy price)
        for all stocks held in non-zero quantity on the requested date.
        If no date is provided, use the current date.
        """
        if date is None:
            date = timezone.now()

        # Ensure the provided date is timezone-aware
        if timezone.is_naive(date):
            date = timezone.make_aware(date)

        # Get all trades up to the given date
        trades = Trade.objects.filter(
            portfolio=self,
            timestamp__lte=date
        ).order_by('stock', 'timestamp')

        # Dictionary to hold FIFO purchase history for each stock
        stock_history = {}

        for trade in trades:
            if trade.stock not in stock_history:
                stock_history[trade.stock] = deque()

            if trade.operation == 'BUY':
                # Add to purchase history with FIFO
                stock_history[trade.stock].append((trade.quantity, trade.price))
            elif trade.operation == 'SELL':
                # Process sale according to FIFO
                quantity_to_sell = trade.quantity
                total_cost = 0
                while quantity_to_sell > 0 and stock_history[trade.stock]:
                    purchased_quantity, purchase_price = stock_history[trade.stock].popleft()
                    if purchased_quantity <= quantity_to_sell:
                        total_cost += purchased_quantity * purchase_price
                        quantity_to_sell -= purchased_quantity
                    else:
                        total_cost += quantity_to_sell * purchase_price
                        stock_history[trade.stock].appendleft((purchased_quantity - quantity_to_sell, purchase_price))
                        quantity_to_sell = 0

        # Prepare the result list
        result = []
        for stock, history in stock_history.items():
            quantity = sum(q for q, _ in history)
            if quantity > 0:
                total_cost = sum(q * p for q, p in history)
                average_buy_price = total_cost / quantity
                result.append((stock, quantity, average_buy_price))
        return result

    def get_invested_value(self, date=None):
        """
        Calculate the invested value of this portfolio, including any sub-portfolios.
        """
        sub_portfolio_value = None
        for sub in self.sub_portfolios.all():
            for stock in sub.get_portfolio_value(date):
                sub_portfolio_value += stock[1]*stock[2]
        #print(f'Subportfolio value: {sub_portfolio_value}')
        #sub_portfolio_value = sum(sub.get_portfolio_value(date) for sub in self.sub_portfolios.all())
        own_value = sum(s[1]*s[2] for s in self.calculate_own_value(date))
        #print(f'Own value: {own_value}')
        return own_value + (sub_portfolio_value or 0)
    
    def get_portfolio_value(self, date=None):
        """
        Calculate the current value of this portfolio, including any sub-portfolios.

        TODO: The results for portfolio on a date must take into account the
        value of scrips on that date.
        """
        sub_portfolio_value = None
        for sub in self.sub_portfolios.all():
            for stock in sub.get_portfolio_value(date):
                sub_portfolio_value += stock[1]*stock[2]
        #print(f'Subportfolio value: {sub_portfolio_value}')
        #sub_portfolio_value = sum(sub.get_portfolio_value(date) for sub in self.sub_portfolios.all())
        own_value = sum(s[1]*s[2] for s in self.calculate_own_value(date))
        #print(f'Own value: {own_value}')
        return own_value + (sub_portfolio_value or 0)

    def add_investment(self, amount):
        # Method to add investment directly to this portfolio
        pass

    def get_portfolio(self, date=None):
        """
        Fetch the constituents of the portfolio, including any sub-portfolios.
        """
        portfolio = self.calculate_own_value(date)
        for sub in self.sub_portfolios.all():
            portfolio += sub.get_portfolio_value(date)

        return portfolio
    
    def get_realized_gains(self, date=None):
        if date is None:
            date = timezone.now()

        # Ensure the provided date is timezone-aware
        if timezone.is_naive(date):
            date = timezone.make_aware(date)

        # Get all trades up to the given date
        trades = Trade.objects.filter(
            portfolio=self,
            timestamp__lte=date
        ).order_by('stock', 'timestamp')

        # Dictionary to hold FIFO purchase history for each stock
        stock_history = {}
        stock_profits = {}
        for trade in trades:
            if trade.stock not in stock_history:
                stock_history[trade.stock] = deque()
            if trade.stock not in stock_profits:
                stock_profits[trade.stock] = 0

            if trade.operation == 'BUY':
                # Add to purchase history with FIFO
                stock_history[trade.stock].append((trade.quantity, trade.price))
            elif trade.operation == 'SELL':
                # Process sale according to FIFO
                quantity_to_sell = trade.quantity
                total_cost = 0
                while quantity_to_sell > 0 and stock_history[trade.stock]:
                    purchased_quantity, purchase_price = stock_history[trade.stock].popleft()
                    if purchased_quantity <= quantity_to_sell:
                        total_cost += purchased_quantity * purchase_price
                        stock_profits[trade.stock] += (purchased_quantity * (trade.price - purchase_price))
                        quantity_to_sell -= purchased_quantity
                    else:
                        total_cost += quantity_to_sell * purchase_price
                        stock_profits[trade.stock] += (quantity_to_sell * (trade.price - purchase_price))
                        stock_history[trade.stock].appendleft((purchased_quantity - quantity_to_sell, purchase_price))
                        quantity_to_sell = 0

        # Prepare the total realized profit
        net_realized_gains = 0
        for stock, gains in stock_profits.items():
            net_realized_gains += gains
        return net_realized_gains

    def get_unrealized_gains(self, date=None):
        pass

    def get_net_gains(self, date=None):
        if date is None:
            date = timezone.now()

        # Ensure the provided date is timezone-aware
        if timezone.is_naive(date):
            date = timezone.make_aware(date)

        # Aggregate buy and sell trades
        trades = Trade.objects.filter(
            timestamp__lte=date,
            portfolio=self
        ).aggregate(
            buy_trades=Sum(
                Case(
                    When(operation="BUY", then=F('quantity') * F('price')),
                    output_field=DecimalField(),
                )
            ),
            sell_trades=Sum(
                Case(
                    When(operation="SELL", then=F('quantity') * F('price')),
                    output_field=DecimalField(),
                )
            )
        )

        buy_trades = trades.get('buy_trades', Decimal('0.00')) or Decimal('0.00')
        sell_trades = trades.get('sell_trades', Decimal('0.00')) or Decimal('0.00')

        return {
            'buy_trades': buy_trades,
            'sell_trades': sell_trades
        }


class Trade(models.Model):
    '''
    Anything bought or sold for money is considered a trade. This affects
    the net value of the portfolio by accounting for the assets other 
    than money in terms of money.
    Buy/Sell equity/futures/options/crypto/commodity
    '''
    TRADE_TYPE_CHOICES = [
        ("BUY", "BUY"),
        ("SELL", "SELL"),
        ("SEED", "SEED")
    ]
    trade_id = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    timestamp = models.DateTimeField()
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=5)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    operation = models.CharField(choices=TRADE_TYPE_CHOICES, max_length=4)
    portfolio = models.ForeignKey(Portfolio, related_name="portfolio", null=False, blank=False, on_delete=models.CASCADE)
    tax = models.DecimalField(max_digits=20, blank=True, decimal_places=2, default=0)
    brokerage = models.DecimalField(max_digits=20, blank=True, decimal_places=2, default=0)

    def __str__(self):
        return "{} {} shares of {} at {}".format(self.operation, self.quantity, self.stock.symbol, self.price)

    def delete(self, *args, **kwargs):
        mappings = TradeTransactionMapping.objects.filter(trade=self)
        for mapping in mappings:
            mapping.transaction.delete()
            mapping.delete()
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        is_new_trade = self.pk is None
        super().save(*args, **kwargs)

        # Handle transactions for the trade
        if is_new_trade:
            self.create_transactions()
        else:
            self.update_transactions()

    def create_transactions(self):
        broker_account = self.portfolio.account  # Assume the portfolio is linked to a broker account
        demat_account = self.portfolio.account.linked_demat_account

        if not demat_account:
            raise ValueError("No Demat account found for the user.")

        trade_value = self.quantity * self.price

        # Create corresponding transactions
        if self.operation == "BUY":
            # Debit from broker account (cash outflow)
            debit = Transaction.objects.create(
                transaction_type="DB",
                source_account=broker_account,
                amount=trade_value + self.tax + self.brokerage,
                timestamp=self.timestamp,
                notes=f"Purchase of {self.quantity} shares of {self.stock.symbol}"
            )
            TradeTransactionMapping.objects.create(trade=self, transaction=debit)

            # Credit to demat account (stock inflow)
            credit = Transaction.objects.create(
                transaction_type="CR",
                asset_type="EQUITY",
                destination_account=demat_account,
                amount=trade_value,
                timestamp=self.timestamp,
                notes=f"Stock credit for {self.quantity} shares of {self.stock.symbol}"
            )
            TradeTransactionMapping.objects.create(trade=self, transaction=credit)

        elif self.operation == "SELL":
            # Credit to broker account (cash inflow)
            credit = Transaction.objects.create(
                transaction_type="CR",
                destination_account=broker_account,
                amount=trade_value - self.tax - self.brokerage,
                timestamp=self.timestamp,
                notes=f"Sale of {self.quantity} shares of {self.stock.symbol}"
            )
            TradeTransactionMapping.objects.create(trade=self, transaction=credit)

            # Debit from demat account (stock outflow)
            debit = Transaction.objects.create(
                transaction_type="DB",
                source_account=demat_account,
                asset_type="EQUITY",
                amount=trade_value,
                timestamp=self.timestamp,
                notes=f"Stock debit for {self.quantity} shares of {self.stock.symbol}"
            )
            TradeTransactionMapping.objects.create(trade=self, transaction=debit)
        
        elif self.operation == "SEED":
            # Seeding the account (or gifted stocks)
            # Credit to demat account (stock inflow)
            seed = Transaction.objects.create(
                transaction_type="CR",
                destination_account=demat_account,
                amount=trade_value,
                asset_type="EQUITY",
                timestamp=self.timestamp,
                notes=f"Stock seeded for {self.quantity} shares of {self.stock.symbol}"
            )
            TradeTransactionMapping.objects.create(trade=self, transaction=seed)

    def update_transactions(self):
        trade_value = self.quantity * self.price

        # Fetch associated transactions via the mapping
        mappings = TradeTransactionMapping.objects.filter(trade=self)
        for mapping in mappings:
            transaction = mapping.transaction

            # Reverse the old transaction's effect before updating it
            if self.operation == 'SELL' and transaction.transaction_type == "CR":
                transaction.destination_account.update_cash_balance(-transaction.amount)
            elif self.operation == 'BUY' and transaction.transaction_type == "DB":
                transaction.source_account.update_cash_balance(transaction.amount)

            # Update the transaction details
            if self.operation == 'BUY':
                if transaction.transaction_type == "CR":
                    transaction.amount = trade_value
                    transaction.notes = f"Stock credit for {self.quantity} shares of {self.stock.symbol}"
                elif transaction.transaction_type == "DB":
                    transaction.amount = trade_value + self.tax + self.brokerage
                    transaction.notes = f"Purchase of {self.quantity} shares of {self.stock.symbol}"
            elif self.operation == 'SELL':
                if transaction.transaction_type == "DB":
                    transaction.amount = trade_value
                    transaction.notes = f"Stock debit for {self.quantity} shares of {self.stock.symbol}"
                elif transaction.transaction_type == "CR":
                    transaction.amount = trade_value - self.tax - self.brokerage
                    transaction.notes = f"Sale of {self.quantity} shares of {self.stock.symbol}"
            elif self.operation == "SEED":
                if transaction.transaction_type == "CR":
                    transaction.amount = trade_value
                    transaction.notes = f"Stock seeded for {self.quantity} shares of {self.stock.symbol}"

            transaction.timestamp = self.timestamp  # Always update the timestamp
            transaction.save()

class Transaction(models.Model):
    """
    Represents any financial transaction, whether an external inflow or an internal transfer.
    """
    TRANSACTION_TYPE_CHOICES = [
        ("CR", "CREDIT"),
        ("DB", "DEBIT"),
        ("TR", "TRANSFER")
    ]

    ASSET_TYPE_CHOICES = [
        ("CASH", "Cash"),
        ("EQUITY", "Equity"),
        ("CRYPTO", "Cryptocurrency"),
        ("COMMODITY", "Commodity"),
        # Add more asset types as needed
    ]

    transaction_id = models.CharField(max_length=20, db_index=True, null=True, blank=True)
    transaction_type = models.CharField(choices=TRANSACTION_TYPE_CHOICES, max_length=8, db_index=True)
    asset_type = models.CharField(choices=ASSET_TYPE_CHOICES, max_length=10, default="CASH", db_index=True)
    source_account = models.ForeignKey(Account, related_name='outgoing_transactions', on_delete=models.CASCADE, null=True, blank=True)
    destination_account = models.ForeignKey(Account, related_name='incoming_transactions', on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    timestamp = models.DateTimeField(db_index=True, default=timezone.now)
    notes = models.TextField(blank=True, null=True)  # Optional notes or external source

    class Meta:
        indexes = [
            models.Index(fields=['transaction_type']),
            models.Index(fields=['asset_type']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['source_account', 'destination_account']),
        ]

    def __str__(self):
        if self.transaction_type == "TR":
            return f"Transfer of {self.amount} {self.get_asset_type_display()} from {self.source_account.name} to {self.destination_account.name} on {self.timestamp}"
        else:
            return f"{self.get_transaction_type_display()} of {self.amount} {self.get_asset_type_display()} to {self.destination_account.name if self.destination_account else 'External'} on {self.timestamp} from {self.source_account.name if self.source_account else 'External'}"
    
    def clean(self):
        asset_related_entities = {
            "EQUITY": "DMAT",
            "CRYPTO": "CRYP",
            "COMMODITY": "CMDT",
        }

        # Validate asset type and corresponding account
        if self.asset_type != "CASH":
            if self.destination_account and asset_related_entities.get(self.asset_type) != self.destination_account.entity:
                raise ValidationError(f"Cannot perform a {self.get_asset_type_display()} transaction on a {self.destination_account.get_entity_display()} account.")

            if self.source_account and asset_related_entities.get(self.asset_type) != self.source_account.entity:
                raise ValidationError(f"Cannot perform a {self.get_asset_type_display()} transaction from a {self.source_account.get_entity_display()} account.")
        
        # Prevent credit transactions in asset-related accounts if asset type is CASH
        if self.asset_type == "CASH" and self.transaction_type in ["CR", "TR"] and self.destination_account and self.destination_account.entity in asset_related_entities.values():
            raise ValidationError(f"Cannot perform a cash credit transaction on a {self.destination_account.get_entity_display()} account.")

        # Validate that there are sufficient funds/assets for debit/transfer
        if self.transaction_type in ["DB", "TR"] and self.asset_type == "CASH" and self.source_account and self.source_account.cash_balance < self.amount:
            raise ValidationError("Cannot withdraw/transfer more money than is present in the account.")
        
        # Additional checks for assets (like ensuring sufficient assets are available) could be added here

    def save(self, *args, **kwargs):
        self.clean()  # Ensure clean is called to validate before saving
        
        # Handle cash balance updates for cash transactions
        if self.asset_type == "CASH":
            if self.transaction_type == "DB" and self.source_account:
                self.source_account.update_cash_balance(-self.amount)
            
            elif self.transaction_type == "CR" and self.destination_account:
                self.destination_account.update_cash_balance(self.amount)

            elif self.transaction_type == "TR":
                if self.source_account:
                    self.source_account.update_cash_balance(-self.amount)
                if self.destination_account:
                    self.destination_account.update_cash_balance(self.amount)

        # For non-cash transactions, other account or asset-specific logic can be applied here

        super().save(*args, **kwargs)

class TradeTransactionMapping(models.Model):
    trade = models.ForeignKey('Trade', on_delete=models.CASCADE)
    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('trade', 'transaction')


class Dividend(models.Model):
    '''
    A dividend is like a CREDIT operation into the account, but the 
    value is determined by the amount of the dividend stocks held on
    the record date. 
    '''
    record_date = models.DateField(null=False, blank = False)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return "Dividend {} for {} on {}".format(self.amount, self.stock.symbol, self.record_date)

    @classmethod
    def get_total_dividend(cls, portfolio, stock, date=None):
        """
        Compute the total dividend for a portfolio and stock up to a given date.
        If no date is provided, use the current date.
        """
        if date is None:
            date = timezone.now()

        # Ensure the provided date is timezone-aware
        if timezone.is_naive(date):
            date = timezone.make_aware(date)

        # Fetch all dividends for the stock
        dividends = cls.objects.filter(stock=stock, record_date__lte=date)

        total_dividend = 0

        for dividend in dividends:
            # Make record_date timezone-aware
            record_date_aware = timezone.make_aware(
                datetime.combine(dividend.record_date, datetime.min.time())
            )

            # Filter trades to get quantities held on record date
            buy_quantity = Trade.objects.filter(
                portfolio=portfolio,
                stock=stock,
                timestamp__lte=record_date_aware,
                operation='BUY'
            ).aggregate(total_buy=Sum('quantity'))['total_buy'] or 0

            sell_quantity = Trade.objects.filter(
                portfolio=portfolio,
                stock=stock,
                timestamp__lte=record_date_aware,
                operation='SELL'
            ).aggregate(total_sell=Sum('quantity'))['total_sell'] or 0

            total_quantity = buy_quantity - sell_quantity
            total_dividend += total_quantity * dividend.amount

        return total_dividend