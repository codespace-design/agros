from django.urls import path
from . import views

urlpatterns = [
    path('', views.estate_list, name='estate-list'),
    path('add/', views.estate_create, name='estate-create'),
    path('<int:pk>/edit/', views.estate_update, name='estate-update'),
    path('<int:pk>/delete/', views.estate_delete, name='estate-delete'),
]
