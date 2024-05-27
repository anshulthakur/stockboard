from django.urls import path, re_path
import webui.views as view

app_name="webui"

urlpatterns = [
    path('', view.index),
]
