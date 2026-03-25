from django.contrib import admin
from .models import ActivityCategory, Activity, TaskAssignment

@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('category', 'plot', 'activity_date')
    list_filter = ('category', 'plot', 'activity_date')

@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ('worker', 'activity', 'task_date', 'status')
    list_filter = ('status', 'task_date')
