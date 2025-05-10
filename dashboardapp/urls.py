from django.urls import path
from .views import DashboardDataAPIViewforcharts,send_to_google_sheet,send_datatosheet, DashbordSamajAPIViewforcards,DashbordSamajAPIViewfortables
from .familyview import FamilyInformationView,FamilyHeadEditView,LoginAPIView,VerifyOTPAPIView,MemberEditView,MemberDeleteView,CreateMemberAPIView

urlpatterns = [
    path('', DashboardDataAPIViewforcharts.as_view()),
    path('dashb_samaj/', DashbordSamajAPIViewforcards.as_view()),
    path('dashb_table/', DashbordSamajAPIViewfortables.as_view()),
    path('send_gs/', send_to_google_sheet),
    path('send_data/', send_datatosheet),
     path('family_profile/<str:phone_number>/', FamilyInformationView.as_view(), name='family-profile'),
     path('family_head_edit/<int:family_head_id>/', FamilyHeadEditView.as_view(), name='family-profile-edit'),
     path('member_edit/<int:member_id>/', MemberEditView.as_view(), name='member-edit'),
     path('member_add/<int:familyhead_id>/', CreateMemberAPIView.as_view(), name='member-add'),
     path('member_delete/<int:member_id>/', MemberDeleteView.as_view(), name='member-delete'),
     path('loginview/', LoginAPIView.as_view(), name='loginview'),
     path('otpview/', VerifyOTPAPIView.as_view(), name='otpview'),
]
# {
#     "phone_number": "1234567890",
#     "otp": "123456"
# }DashbordSamajAPIViewfortables
