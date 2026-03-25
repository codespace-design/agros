from django.contrib import admin
from .models import Production

@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ('plot', 'harvest_date', 'quantity')
    list_filter = ('plot', 'harvest_date')
