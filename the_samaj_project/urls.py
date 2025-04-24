"""
URL configuration for the_samaj_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path, re_path,include
from testapp import views
# from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
# from your_app.views import custom_404

handler404 = 'testapp.views.custom_404'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login_view/',views.login_view,name='login_view'),
    path('register_view/',views.register_view,name='register_view'),
    path('otp_view/',views.otp_view,name='otp_view'),
    path('', views.create_family, name='create_family'),
    path('family_list/<int:family_id>/',views.family_list,name='family_list'),
    # re_path(r'^family_list/(?P<family_id>\d+)(?:/(?P<extra>.+))?/$', views.family_list, name='family_list'),
    path('update_family/<int:family_id>/', views.update_family, name='update_family'),
    path('delete_family/<int:family_id>/', views.delete_family, name='delete_family'),
    path('create_familyhead/<int:family_id>/',views.create_familyhead, name='create_familyhead'),
    path('familyhead_list/<int:familyhead_id>/', views.familyhead_list, name='familyhead_list'),
    path('familyhead_template/<int:familyhead_id>/', views.familyhead_template, name='familyhead_template'),
    path('update_familyhead/<int:familyhead_id>/',views.update_familyhead, name='update_familyhead'),
    path('delete_familyhead/<int:familyhead_id>/',views.delete_familyhead, name='delete_familyhead'),
    path('create_member/<int:familyhead_id>/', views.create_member, name='create_member'),
    path('member_list/<int:familyhead_id>/', views.member_list, name='member_list'),
    path('update_member/<int:member_id>/', views.update_member, name='update_member'),
    path('delete_member/<int:member_id>/', views.delete_member, name='delete_member'),
    path('detail_member/<int:member_id>/', views.detail_member, name='detail_member'),
    path('get_districts/<int:state_id>/', views.get_districts, name='get_districts'),
    path("save_form_view/", views.save_form_view, name="save_form_view"),
    path("save-form-data/", views.save_form_data, name="save_form_data"),
    path("dashboard/", views.samaj_dashboard, name="samaj_dashboard"),
    path('apidashboard/', include('dashboardapp.urls')),
    
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
