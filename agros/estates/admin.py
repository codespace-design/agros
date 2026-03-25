from django.contrib import admin
from .models import Estate

@admin.register(Estate)
class EstateAdmin(admin.ModelAdmin):
    list_display = ('estate_name', 'location', 'total_area')
