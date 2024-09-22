from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView
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
router.register(r'bulk-trades', views.BulkTradeViewSet, basename='bulk-trade')
router.register(r'dividends', views.DividendViewSet, basename='dividend')


app_name="portfolio"

urlpatterns = [
    path('overview', views.overview, name="portfolio-overview"),
    path('accounts', views.accounts, name="accounts-page"),
    path('portfolios', views.portfolios, name="portfolios-page"),
    path('<str:asset_type>/wallet', views.wallets, name="wallet-page"),
    path('<str:asset_type>/orders', views.orderbook, name="orders-page"),
    path('api/user/summary/', views.UserFinancialOverviewView.as_view(), name='net-worth'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='portfolio:schema'), name='swagger'),
    path("api/", include((router.urls))),
    path("lander", views.temp, name="landing"),
]
