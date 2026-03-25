from django.urls import path
from . import views

urlpatterns = [
    path('', views.production_list, name='production-list'),
    path('add/', views.production_create, name='production-create'),
]
