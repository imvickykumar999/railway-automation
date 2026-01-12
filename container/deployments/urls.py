from django.urls import path
from . import views

app_name = 'deployments'

urlpatterns = [
    path('', views.deployment_list, name='deployment_list'),
    path('new/', views.deployment_form, name='deployment_form'),
    path('<int:pk>/', views.deployment_detail, name='deployment_detail'),
    path('<int:pk>/edit/', views.deployment_edit, name='deployment_edit'),
    path('<int:pk>/delete/', views.deployment_delete, name='deployment_delete'),
    path('<int:pk>/deploy/', views.deployment_deploy, name='deployment_deploy'),
    path('<int:pk>/logs/', views.deployment_logs, name='deployment_logs'),
]

