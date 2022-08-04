from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('check/', views.check, name='check'),
    path('rbd/', views.rbd, name='rbd'),
    path('rbds/', views.rbds, name='rbds'),
    path('report/', views.report, name='report'),
    path('upload/', views.upload, name='upload'),
    path('check_result/', views.check_result, name='upload'),

    path('signin', views.signin),
    path('user_info/', views.user_info)

]