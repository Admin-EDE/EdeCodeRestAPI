from django.urls import path

from . import views
from . import views_api

urlpatterns = [
    path('login/', views.login, name='login'),
    path('check/', views.check, name='check'),

    path('users/', views_api.users, name='users'),
    path('rbd/', views_api.rbd, name='rbd'),
    path('rbds/', views_api.rbds, name='rbds'),
    path('report/', views_api.report, name='report'),

    path('upload', views.upload, name='upload'),
    path('check_result/', views.check_result, name='upload'),

    path('signin', views_api.signin),
    path('user_info/', views_api.user_info)

]