from django.contrib import admin
from .models import Plot

@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):
    list_display = ('plot_name', 'estate', 'plant_count')
    list_filter = ('estate',)
