from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from agros.utils import log_action
from .models import Labor, Attendance
from .forms import LaborForm, AttendanceForm

def is_admin(user):
    return user.role == 'ADMIN' or user.is_superuser

def is_manager_or_admin(user):
    return user.role in ['ADMIN', 'MANAGER'] or user.is_superuser

@login_required
def labor_list(request):
    labors = Labor.objects.all()
    return render(request, 'labor/labor_list.html', {'labors': labors})

@login_required
@user_passes_test(is_manager_or_admin)
def labor_create(request):
    if request.method == "POST":
        form = LaborForm(request.POST)
        if form.is_valid():
            labor = form.save()
            log_action(request.user, labor, ADDITION, f"Added Worker: {labor.name}")
            messages.success(request, f"Worker profile for '{labor.name}' added successfully.")
            return redirect('labor-list')
    else:
        form = LaborForm()
    return render(request, 'labor/labor_form.html', {'form': form, 'title': 'Add Labor'})

@login_required
@user_passes_test(is_manager_or_admin)
def labor_update(request, pk):
    labor = get_object_or_404(Labor, pk=pk)
    if request.method == "POST":
        form = LaborForm(request.POST, instance=labor)
        if form.is_valid():
            form.save()
            log_action(request.user, labor, CHANGE, f"Updated Worker: {labor.name}")
            messages.success(request, f"Worker profile for '{labor.name}' updated successfully.")
            return redirect('labor-list')
    else:
        form = LaborForm(instance=labor)
    return render(request, 'labor/labor_form.html', {'form': form, 'title': 'Edit Labor'})

@login_required
@user_passes_test(is_manager_or_admin)
def labor_delete(request, pk):
    labor = get_object_or_404(Labor, pk=pk)
    if request.method == "POST":
        name = labor.name
        log_action(request.user, labor, DELETION, f"Deleted Worker: {name}")
        labor.delete()
        messages.warning(request, f"Worker '{name}' has been removed from the roster.")
        return redirect('labor-list')
    return render(request, 'labor/labor_confirm_delete.html', {'labor': labor})

@login_required
@user_passes_test(is_manager_or_admin)
def attendance_list(request):
    records = Attendance.objects.select_related('worker').order_by('-date')
    
    filter_date = request.GET.get('date')
    if filter_date:
        records = records.filter(date=filter_date)
        
    return render(request, 'labor/attendance_list.html', {
        'records': records,
        'filter_date': filter_date
    })

@login_required
@user_passes_test(is_manager_or_admin)
def attendance_create(request):
    from django.utils import timezone
    today = timezone.localdate()
    
    # We pass all active labor profiles down to the template to render the sheet rows
    labors = Labor.objects.all().order_by('name')
    
    if request.method == "POST":
        target_date_str = request.POST.get('target_date')
        if not target_date_str:
            target_date = today
        else:
            from datetime import datetime
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            
        # Iterate over submitted form items dynamically
        updated_count = 0
        for labor in labors:
            status = request.POST.get(f'status_{labor.id}')
            if status in dict(Attendance.STATUS_CHOICES).keys():
                # Perform an update or create logic
                record, created = Attendance.objects.update_or_create(
                    worker=labor,
                    date=target_date,
                    defaults={'status': status}
                )
                action = ADDITION if created else CHANGE
                log_action(request.user, record, action, f"Marked Attendance on {target_date}: {status}")
                updated_count += 1
        messages.success(request, f"Attendance synced for {updated_count} workers on {target_date}.")
        return redirect('attendance-list')
        
    return render(request, 'labor/attendance_bulk.html', {
        'labors': labors, 
        'today': today.strftime("%Y-%m-%d"),
        'title': 'Bulk Mark Attendance'
    })

@login_required
@user_passes_test(is_manager_or_admin)
def payroll_summary(request):
    from django.db.models import Sum
    from activities.models import TaskAssignment
    
    labors = Labor.objects.all()
    payroll_data = []
    
    for labor in labors:
        # Calculate total earned from completed tasks
        total_earned = TaskAssignment.objects.filter(
            worker=labor, 
            status='COMPLETED'
        ).aggregate(total=Sum('wage'))['total'] or 0
        
        # Calculate total paid from Payment records
        total_paid = labor.payments.aggregate(total=Sum('amount'))['total'] or 0
        
        balance_due = total_earned - total_paid
        
        payroll_data.append({
            'labor': labor,
            'total_earned': total_earned,
            'total_paid': total_paid,
            'balance_due': balance_due
        })
        
    return render(request, 'labor/payroll_list.html', {
        'payroll_data': payroll_data,
        'title': 'Employee Payroll'
    })

@login_required
@user_passes_test(is_manager_or_admin)
def record_payment(request):
    from .forms import PaymentForm
    from django.contrib.admin.models import ADDITION
    from agros.utils import log_action
    from django.db.models import Sum
    from activities.models import TaskAssignment
    
    # Generate payroll summary for the slip
    payroll_data = {}
    for labor in Labor.objects.all():
        total_earned = float(TaskAssignment.objects.filter(worker=labor, status='COMPLETED').aggregate(total=Sum('wage'))['total'] or 0)
        total_paid = float(labor.payments.aggregate(total=Sum('amount'))['total'] or 0)
        balance_due = total_earned - total_paid
        payroll_data[labor.id] = {
            'total_earned': total_earned,
            'total_paid': total_paid,
            'balance_due': balance_due
        }
        
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            log_action(request.user, payment, ADDITION, f"Recorded Payment to {payment.worker.name}: ₹{payment.amount}")
            messages.success(request, f"Payment of ₹{payment.amount} to {payment.worker.name} recorded.")
            return redirect('payroll-summary')
    else:
        # Pre-select worker if passed in GET
        worker_id = request.GET.get('worker')
        initial = {}
        if worker_id:
            initial['worker'] = worker_id
        form = PaymentForm(initial=initial)
        
    return render(request, 'labor/payment_form.html', {
        'form': form,
        'title': 'Record Payment',
        'payroll_data': payroll_data
    })

@login_required
@user_passes_test(is_admin)
def manager_payroll_summary(request):
    from django.db.models import Sum
    from users.models import User
    
    managers = User.objects.filter(role='MANAGER', is_active=True)
    payroll_data = []
    
    for manager in managers:
        # Calculate total paid from Payment records linked directly to this Manager
        total_paid = manager.manager_payments.aggregate(total=Sum('amount'))['total'] or 0
        
        payroll_data.append({
            'manager': manager,
            'total_paid': total_paid
        })
        
    return render(request, 'labor/manager_payroll_list.html', {
        'payroll_data': payroll_data,
        'title': 'Manager Payroll Disbursement'
    })

@login_required
@user_passes_test(is_admin)
def record_manager_payment(request):
    from .forms import ManagerPaymentForm
    from django.contrib.admin.models import ADDITION
    from agros.utils import log_action
    
    if request.method == "POST":
        form = ManagerPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            manager_name = payment.manager.username if payment.manager else "Unknown Manager"
            log_action(request.user, payment, ADDITION, f"Recorded Payment to Manager {manager_name}: ₹{payment.amount}")
            messages.success(request, f"Payment of ₹{payment.amount} to Manager {manager_name} recorded.")
            return redirect('manager-payroll-summary')
    else:
        # Pre-select manager if passed in GET
        manager_id = request.GET.get('manager')
        initial = {}
        if manager_id:
            initial['manager'] = manager_id
        form = ManagerPaymentForm(initial=initial)
        
    return render(request, 'labor/payment_form.html', {
        'form': form,
        'title': 'Record Manager Compensation',
        'is_manager_form': True
    })
@login_required
@user_passes_test(is_manager_or_admin)
def export_attendance_csv(request):
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Agros_Attendance_Report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['AGROS - Global Attendance Report'])
    writer.writerow([])
    writer.writerow(['Worker Name', 'Date', 'Status'])
    
    for record in Attendance.objects.select_related('worker').order_by('-date'):
        writer.writerow([record.worker.name, record.date, record.get_status_display()])
        
    return response

@login_required
@user_passes_test(is_manager_or_admin)
def export_attendance_pdf(request):
    from django.http import HttpResponse
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import letter
    from django.conf import settings
    import os
    import time
    import uuid
    
    unique_id = str(uuid.uuid4())[:8].upper()
    doc_title = f"AGROS_Attendance_Report_{unique_id}"
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{doc_title}.pdf"'
    
    doc = SimpleDocTemplate(
        response, 
        pagesize=letter,
        title=doc_title,
        author="AGROS System"
    )
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=15,
        alignment=1
    )
    
    # Add Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'agros_logo.png')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=1*28.35, height=1*28.35)
        elements.append(img)
        elements.append(Spacer(1, 15))

    elements.append(Paragraph("AGROS - Global Attendance Report", title_style))
    elements.append(Spacer(1, 10))
    
    # Table Style
    t_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f8f9fa")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkcyan),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#fdfdfd")])
    ])
    
    data = [['Date', 'Worker Name', 'Status']]
    for record in Attendance.objects.select_related('worker').order_by('-date')[:500]: # Safety limit
        data.append([
            record.date.strftime("%b %d, %Y"), 
            record.worker.name, 
            record.get_status_display()
        ])
    
    if len(data) > 1:
        table = Table(data, colWidths=[100, 200, 100])
        table.setStyle(t_style)
        elements.append(table)
    else:
        elements.append(Paragraph("<i>No attendance records found.</i>", styles['Normal']))

    doc.build(elements)
    return response
@login_required
@user_passes_test(is_manager_or_admin)
def export_payroll_csv(request):
    import csv
    from django.http import HttpResponse
    from django.db.models import Sum
    from activities.models import TaskAssignment
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Agros_Labor_Payroll_Report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['AGROS - Global Labor Payroll Report'])
    writer.writerow([])
    writer.writerow(['Worker Name', 'Total Earned', 'Total Paid', 'Balance Due'])
    
    for labor in Labor.objects.all():
        total_earned = TaskAssignment.objects.filter(worker=labor, status='COMPLETED').aggregate(total=Sum('wage'))['total'] or 0
        total_paid = labor.payments.aggregate(total=Sum('amount'))['total'] or 0
        balance_due = total_earned - total_paid
        writer.writerow([labor.name, f"Rs.{total_earned}", f"Rs.{total_paid}", f"Rs.{balance_due}"])
        
    return response

@login_required
@user_passes_test(is_manager_or_admin)
def export_payroll_pdf(request):
    from django.http import HttpResponse
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import letter
    from django.db.models import Sum
    from activities.models import TaskAssignment
    from django.conf import settings
    import os
    import time
    import uuid
    
    unique_id = str(uuid.uuid4())[:8].upper()
    doc_title = f"AGROS_Payroll_Report_{unique_id}"
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{doc_title}.pdf"'
    
    doc = SimpleDocTemplate(
        response, 
        pagesize=letter,
        title=doc_title,
        author="AGROS System"
    )
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=15,
        alignment=1
    )
    
    # Add Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'agros_logo.png')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=1*28.35, height=1*28.35)
        elements.append(img)
        elements.append(Spacer(1, 15))

    elements.append(Paragraph("AGROS - Global Labor Payroll Report", title_style))
    elements.append(Spacer(1, 10))
    
    # Table Style
    t_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f8f9fa")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkcyan),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#fdfdfd")])
    ])
    
    data = [['Worker Name', 'Total Earned', 'Total Paid', 'Balance Due']]
    
    for labor in Labor.objects.all()[:500]: # Safety limit
        total_earned = float(TaskAssignment.objects.filter(worker=labor, status='COMPLETED').aggregate(total=Sum('wage'))['total'] or 0)
        total_paid = float(labor.payments.aggregate(total=Sum('amount'))['total'] or 0)
        balance_due = total_earned - total_paid
        
        data.append([
            labor.name, 
            f"Rs.{total_earned:.2f}", 
            f"Rs.{total_paid:.2f}", 
            f"Rs.{balance_due:.2f}"
        ])
    
    if len(data) > 1:
        table = Table(data, colWidths=[160, 100, 100, 100])
        table.setStyle(t_style)
        elements.append(table)
    else:
        elements.append(Paragraph("<i>No payroll records found.</i>", styles['Normal']))

    doc.build(elements)
    return response
