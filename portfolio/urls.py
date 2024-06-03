from django.urls import path, re_path
import portfolio.views as view

app_name="portfolio"

urlpatterns = [
    path('', view.index),
]
