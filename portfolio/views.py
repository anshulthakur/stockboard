from django.shortcuts import 
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from portfolio.serializers import *
from datetime import timedelta, datetime

# Create your views here.
def index(request):
    return render(request, "portfolio/index.html")

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited
    """
    queryset = Group.objects.all().order_by('id')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all().order_by('id')
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = '__all__'

class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.all().order_by('id')
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = '__all__'

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('id')
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = '__all__'

    filterset_fields = ['timestamp']

    def get_queryset(self):
        queryset = self.queryset
        print(self.request.query_params)
        date_start_filter = self.request.query_params.get('date_start')
        date_end_filter = self.request.query_params.get('date_end')

        if date_start_filter:
            # Filter tasks by 'date_started'
            queryset = queryset.filter(timestamp__geq=date_start_filter)
        if date_end_filter:
            queryset = queryset.filter(timestamp__leq=date_end_filter)

        return queryset


class TradeViewSet(viewsets.ModelViewSet):
    queryset = Trade.objects.all().order_by('id')
    serializer_class = TradeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = '__all__'

    filterset_fields = ['timestamp']

    def get_queryset(self):
        queryset = self.queryset
        print(self.request.query_params)
        date_start_filter = self.request.query_params.get('date_start')
        date_end_filter = self.request.query_params.get('date_end')

        if date_start_filter:
            # Filter tasks by 'date_started'
            queryset = queryset.filter(timestamp__geq=date_start_filter)
        if date_end_filter:
            queryset = queryset.filter(timestamp__leq=date_end_filter)

        return queryset

class DividendViewSet(viewsets.ModelViewSet):
    queryset = Dividend.objects.all().order_by('id')
    serializer_class = DividendSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = '__all__'

    filterset_fields = ['record_date']

    def get_queryset(self):
        queryset = self.queryset
        print(self.request.query_params)
        date_start_filter = self.request.query_params.get('date_start')
        date_end_filter = self.request.query_params.get('date_end')

        if date_start_filter:
            # Filter tasks by 'date_started'
            queryset = queryset.filter(record_date__geq=date_start_filter)
        if date_end_filter:
            queryset = queryset.filter(record_date__leq=date_end_filter)

        return queryset