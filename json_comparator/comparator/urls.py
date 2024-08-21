from django.urls import path
from .views import compare_json

urlpatterns = [
    path('compare-json/', compare_json, name='compare_json'),
]
