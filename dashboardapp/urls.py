from django.urls import path
from .views import DashboardDataAPIView,send_to_google_sheet,send_datatosheet
from .familyview import FamilyInformationView

urlpatterns = [
    path('', DashboardDataAPIView.as_view()),
    path('send_gs/', send_to_google_sheet),
    path('send_data/', send_datatosheet),
     path('family_profile/<str:phone_number>/', FamilyInformationView.as_view(), name='family-profile'),
]
