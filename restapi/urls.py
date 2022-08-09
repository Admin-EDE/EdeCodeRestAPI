from django.urls import path

from . import views
from . import views_api

urlpatterns = [

    path('check/', views.check, name='check'),
    path('upload', views.upload, name='upload'),
    path('check_result/<str:report_id>/', views.check_result, name='upload'),

    path('login/', views_api.login_view, name='login'),
    path('users/', views_api.users, name='users'),
    path('rbd/<int:rbd_id>/', views_api.rbd, name='rbd'),
    path('rbds/', views_api.rbds, name='rbds'),
    path('report/<str:report_id>/', views_api.report, name='report'),

]