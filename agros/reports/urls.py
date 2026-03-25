from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_list, name='report-list'),
    path('export/csv/', views.export_csv, name='report-export-csv'),
    path('export/pdf/', views.export_pdf, name='report-export-pdf'),
]
