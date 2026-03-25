from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_list, name='user-list'),
    path('add/', views.user_create, name='user-create'),
    path('<int:pk>/edit/', views.user_update, name='user-update'),
    path('<int:pk>/approve/', views.user_approve, name='user-approve'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_manage, name='settings-manage'),
    path('audit-log/', views.activity_log, name='activity-log'),
]
