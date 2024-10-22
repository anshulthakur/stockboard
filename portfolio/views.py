from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from portfolio.serializers import *
from datetime import timedelta, datetime

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.decorators import login_required

def temp(request):
    return render(request, "portfolio/lander.html", context={})

@login_required
def overview(request):
    enabled_modules = {'Stocks': {},
                       'Crypto': {},
                       'Commodity': {},
                       }
    context = {'entries': enabled_modules,
               'module': 'overview', }
    return render(request, "portfolio/render.html", context=context)

@login_required
def accounts(request):
    enabled_modules = {'Stocks': {},
                       'Crypto': {},
                       'Commodity': {},
                       }
    context = {'entries': enabled_modules,
               'module': 'accounts', }
    return render(request, "portfolio/render.html", context=context)

@login_required
def portfolios(request):
    enabled_modules = {'Stocks': {},
                       'Crypto': {},
                       'Commodity': {},
                       }
    context = {'entries': enabled_modules,
               'module': 'portfolios', }
    return render(request, "portfolio/render.html", context=context)

@login_required
def wallets(request, asset_type):
    enabled_modules = {'Stocks': {},
                       'Crypto': {},
                       'Commodity': {},
                       }
    context = {'entries': enabled_modules,
               'asset': asset_type,
               'module': 'wallet', }
    return render(request, "portfolio/render.html", context=context)

@login_required
def orderbook(request, asset_type):
    enabled_modules = {'Stocks': {},
                       'Crypto': {},
                       'Commodity': {},
                       }
    context = {'entries': enabled_modules,
               'asset': asset_type,
               'module': 'orders', }
    return render(request, "portfolio/render.html", context=context)

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited
    """
    queryset = Group.objects.all().order_by('id')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MarketViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows market objects to be viewed or edited
    """
    queryset = Market.objects.all().order_by('id')
    serializer_class = MarketSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    

class StockViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows market objects to be viewed or edited
    """
    queryset = Stock.objects.all().order_by('id')
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['symbol', 'market__name']  # Supports partial matching on these fields

    def get_queryset(self):
        queryset = self.queryset
        #print(self.request.query_params)
        symbol = self.request.query_params.get('symbol')
        market = self.request.query_params.get('market')
        
        if symbol:
            queryset = queryset.filter(symbol__contains=symbol)
        return queryset
    
class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all().order_by('id')
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = '__all__'

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        # Pass the request context to the serializer
        return {'request': self.request}

class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.all().order_by('id')
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = '__all__'

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('timestamp')
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = '__all__'
    filterset_fields = ['source_account', 'destination_account', 'transaction_type', 'timestamp']

    def get_queryset(self):
        queryset = self.queryset
        #print(self.request.query_params)
        account_id = self.request.query_params.get('account_id')
        date_start_filter = self.request.query_params.get('date_start')
        date_end_filter = self.request.query_params.get('date_end')
        
        if account_id:
            queryset = queryset.filter(source_account_id=account_id) | queryset.filter(destination_account_id=account_id)
        if date_start_filter:
            # Filter tasks by 'date_started'
            queryset = queryset.filter(timestamp__geq=date_start_filter)
        if date_end_filter:
            queryset = queryset.filter(timestamp__leq=date_end_filter)
        return queryset
    
    # def partial_update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)

class BulkTradeViewSet(viewsets.ModelViewSet):
    queryset = Trade.objects.all().order_by('timestamp')
    serializer_class = BulkTradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TradeViewSet(viewsets.ModelViewSet):
    queryset = Trade.objects.all().order_by('timestamp')
    serializer_class = TradeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = '__all__'

    filterset_fields = ['timestamp', 'portfolio', 'stock']

    def get_queryset(self):
        queryset = self.queryset
        #queryset = super().get_queryset()
        #print(self.request.query_params)
        date_start_filter = self.request.query_params.get('date_start')
        date_end_filter = self.request.query_params.get('date_end')
        portfolio_filter = self.request.query_params.get('portfolio_id')
        symbol = self.request.query_params.get('search')
        if date_start_filter:
            # Filter tasks by 'date_started'
            queryset = queryset.filter(timestamp__geq=date_start_filter)
        if date_end_filter:
            queryset = queryset.filter(timestamp__leq=date_end_filter)
        if portfolio_filter:
            queryset = queryset.filter(portfolio__id=portfolio_filter)
        if symbol:
            queryset = queryset.filter(stock__symbol__icontains=symbol)
        for q in queryset:
            print(q)
        return queryset
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class CustomPagination(PageNumberPagination):
    page_size = 150
    max_page_size = 500

class HoldingsViewSet(viewsets.ViewSet):
    serializer_class = HoldingSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['symbol', 'name']
    pagination_class = CustomPagination
    queryset = Portfolio.objects.none()  # Dummy queryset to satisfy permission check
    filterset_fields = ['timestamp', 'portfolio', 'symbol']

    def list(self, request, portfolio_id):
        portfolio = Portfolio.objects.get(id=portfolio_id)
        holdings = portfolio.get_portfolio()
        
        members = [{'stock': member[0], 'symbol':member[3], 'shares': member[1], 'price': member[2], 'cost': 0, 'cmp': member[4], 'value': 0, 'pnl': 0, 'day_change': 0} for member in holdings]
        members = sorted(members, key=lambda x: x['symbol'])
        # Apply search filtering
        symbol = request.query_params.get('symbol', None)
        stock = request.query_params.get('stock', None)
        if symbol is not None:
            members = [member for member in members if symbol.lower() in member['symbol'].lower()]
        if stock is not None:
            members = [member for member in members if stock.upper() in member['stock'].upper()]
        for member in members:
            member['value'] = float(member['cmp'])*float(member['shares'])
            member['pnl'] = float(member['cmp'] - member['price'])*float(member['shares'])

        # Paginate the list manually
        paginator = CustomPagination()
        page = paginator.paginate_queryset(members, request)

        serializer = HoldingSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

class DividendViewSet(viewsets.ModelViewSet):
    queryset = Dividend.objects.all().order_by('record_date')
    serializer_class = DividendSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = '__all__'

    filterset_fields = ['record_date']

    def get_queryset(self):
        queryset = self.queryset
        #print(self.request.query_params)
        date_start_filter = self.request.query_params.get('date_start')
        date_end_filter = self.request.query_params.get('date_end')

        if date_start_filter:
            # Filter tasks by 'date_started'
            queryset = queryset.filter(record_date__geq=date_start_filter)
        if date_end_filter:
            queryset = queryset.filter(record_date__leq=date_end_filter)

        return queryset
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
class UserFinancialOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # The instance is the user, or any object that your serializer needs.
        user = request.user

        # Pass the instance to the serializer
        serializer = UserFinancialOverviewSerializer(instance=user, context={'request': request})

        # Return the serialized data
        return Response(serializer.data)