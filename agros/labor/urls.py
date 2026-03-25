from django.urls import path
from . import views

urlpatterns = [
    path('', views.labor_list, name='labor-list'),
    path('add/', views.labor_create, name='labor-create'),
    path('<int:pk>/edit/', views.labor_update, name='labor-update'),
    path('<int:pk>/delete/', views.labor_delete, name='labor-delete'),
    
    # Attendance
    path('attendance/', views.attendance_list, name='attendance-list'),
    path('attendance/mark/', views.attendance_create, name='attendance-create'),
    path('attendance/export/csv/', views.export_attendance_csv, name='attendance-export-csv'),
    path('attendance/export/pdf/', views.export_attendance_pdf, name='attendance-export-pdf'),
    
    # Payroll & Payments
    path('payroll/', views.payroll_summary, name='payroll-summary'),
    path('payroll/pay/', views.record_payment, name='record-payment'),
    path('payroll/export/csv/', views.export_payroll_csv, name='payroll-export-csv'),
    path('payroll/export/pdf/', views.export_payroll_pdf, name='payroll-export-pdf'),
    
    # Manager Payroll (Admin Only)
    path('manager-payroll/', views.manager_payroll_summary, name='manager-payroll-summary'),
    path('manager-payroll/pay/', views.record_manager_payment, name='record-manager-payment'),
]
