from django.urls import path

from . import views
from . import views_api

urlpatterns = [

    path('check/', views.check, name='restapi_check'),
    path('upload', views.upload, name='restapi_upload'),
    path('check_result/<str:report_id>/', views.check_result, name='restapi_upload'),
    path('success/', views.success_view, name='restapi_success'),

    path('login/', views_api.login_view, name='restapi_api_login'),
    path('users/', views_api.users, name='restapi_api_users'),
    path('rbd/<int:rbd_id>/', views_api.rbd, name='restapi_api_rbd'),
    path('rbds/', views_api.rbds, name='restapi_api_rbds'),
    path('report/<str:report_id>/', views_api.report, name='restapi_api_report'),

]