from django.contrib import admin
from django.urls import path, include
from .views import dashboard, landing, mark_task_complete
from . import views
from users.views import logout_view, signup, custom_login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing, name='landing'),
    path('dashboard/', dashboard, name='dashboard'),
    path('task/<int:task_id>/complete/', views.mark_task_complete, name='complete-task'),
    
    # Auth
    path('login/', custom_login, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup, name='signup'),
    
    # App URLs
    path('users/', include('users.urls')),
    path('estates/', include('estates.urls')),
    path('plots/', include('plots.urls')),
    path('activities/', include('activities.urls')),
    path('labor/', include('labor.urls')),
    path('production/', include('production.urls')),
    path('reports/', include('reports.urls')),
]
