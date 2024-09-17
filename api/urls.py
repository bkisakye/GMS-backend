from django.urls import path
from .views import get_districts

urlpatterns = [
    path("districts/", get_districts, name="get_districts"),
]
