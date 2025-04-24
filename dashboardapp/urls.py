from django.urls import path
from .views import DashboardDataAPIView

urlpatterns = [
    path('', DashboardDataAPIView.as_view()),
]
