from django.urls import path
from . import views

urlpatterns = [
    path('', views.plot_list, name='plot-list'),
    path('add/', views.plot_create, name='plot-create'),
    path('<int:pk>/edit/', views.plot_update, name='plot-update'),
    path('<int:pk>/delete/', views.plot_delete, name='plot-delete'),
]
