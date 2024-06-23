from django.urls import path, include
import portfolio.views as views
from rest_framework import routers



router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'groups', views.GroupViewSet, basename='group')
router.register(r'stocks', views.StockViewSet, basename='stock')
router.register(r'markets', views.MarketViewSet, basename='market')
router.register(r'accounts', views.AccountViewSet, basename='account')
router.register(r'portfolios', views.PortfolioViewSet, basename='portfolio')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'trades', views.TradeViewSet, basename='trade')
router.register(r'dividends', views.DividendViewSet, basename='dividend')


app_name="portfolio"

urlpatterns = [
    path('overview/', views.index, name="portfolio-overview"),
    path("api/", include((router.urls))),
]
