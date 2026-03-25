from django.contrib import admin
from .models import Labor

@admin.register(Labor)
class LaborAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')
