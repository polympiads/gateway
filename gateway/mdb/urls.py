from django.urls import path

from .views import mdbping

urlpatterns = [
    path('mdbping', mdbping.mdbping)
]