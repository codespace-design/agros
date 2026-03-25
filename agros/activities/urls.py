from django.urls import path
from . import views

urlpatterns = [
    # Categories
    path('categories/', views.category_list, name='category-list'),
    path('categories/add/', views.category_create, name='category-create'),
    
    # Activities
    path('', views.activity_list, name='activity-list'),
    path('record/', views.activity_create, name='activity-create'),
    
    # Tasks
    path('tasks/', views.task_list, name='task-list'),
    path('tasks/assign/', views.task_assign, name='task-assign'),
]
