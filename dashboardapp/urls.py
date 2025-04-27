from django.urls import path
from .views import DashboardDataAPIView,send_to_google_sheet

urlpatterns = [
    path('', DashboardDataAPIView.as_view()),
    path('send_gs/', send_to_google_sheet),
]
