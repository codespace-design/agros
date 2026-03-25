import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.http import HttpResponse
from django.conf import settings
import os

from production.models import Production
from activities.models import Activity, TaskAssignment
from estates.models import Estate
from plots.models import Plot

def is_admin(user):
    return user.role == 'ADMIN' or user.is_superuser

@login_required
def report_list(request):
    # Basic filters
    estate_id = request.GET.get('estate')
    plot_id = request.GET.get('plot')
    filter_date = request.GET.get('date')
    
    productions = Production.objects.all()
    activities = Activity.objects.all()
    
    if estate_id:
        productions = productions.filter(plot__estate_id=estate_id)
        activities = activities.filter(plot__estate_id=estate_id)
    if plot_id:
        productions = productions.filter(plot_id=plot_id)
        activities = activities.filter(plot_id=plot_id)
    if filter_date:
        productions = productions.filter(harvest_date=filter_date)
        activities = activities.filter(activity_date=filter_date)
        
    production_summary = productions.values('plot__plot_name').annotate(total_qty=Sum('quantity'))
    
    context = {
        'production_summary': production_summary,
        'estates': Estate.objects.all(),
        'plots': Plot.objects.all(),
        'selected_estate': estate_id,
        'selected_plot': plot_id,
        'filter_date': filter_date,
    }
    return render(request, 'reports/report_list.html', context)

@login_required
@user_passes_test(is_admin)
def export_csv(request):
    estate_id = request.GET.get('estate', '')
    plot_id = request.GET.get('plot', '')
    filter_date = request.GET.get('date', '')

    activities = Activity.objects.all()
    productions = Production.objects.all()

    if estate_id:
        activities = activities.filter(plot__estate_id=estate_id)
        productions = productions.filter(plot__estate_id=estate_id)
    if plot_id:
        activities = activities.filter(plot_id=plot_id)
        productions = productions.filter(plot_id=plot_id)
    if filter_date:
        activities = activities.filter(activity_date=filter_date)
        productions = productions.filter(harvest_date=filter_date)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Agros_Report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['AGROS - Comprehensive Agricultural Report'])
    writer.writerow([]) # Empty spacer row
    writer.writerow(['Type', 'Estate', 'Plot', 'Date', 'Details', 'Quantity/Information'])
    
    for act in activities:
        writer.writerow(['Activity', act.plot.estate.estate_name, act.plot.plot_name, act.activity_date, act.category.category_name, act.description])
        
    for prod in productions:
        writer.writerow(['Production', prod.plot.estate.estate_name, prod.plot.plot_name, prod.harvest_date, 'N/A', f"{prod.quantity} kg"])
        
    return response

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.conf import settings
import os

@login_required
@user_passes_test(is_admin)
def export_pdf(request):
    estate_id = request.GET.get('estate', '')
    plot_id = request.GET.get('plot', '')
    filter_date = request.GET.get('date', '')

    activities = Activity.objects.all()
    productions = Production.objects.all()

    if estate_id:
        activities = activities.filter(plot__estate_id=estate_id)
        productions = productions.filter(plot__estate_id=estate_id)
    if plot_id:
        activities = activities.filter(plot_id=plot_id)
        productions = productions.filter(plot_id=plot_id)
    if filter_date:
        activities = activities.filter(activity_date=filter_date)
        productions = productions.filter(harvest_date=filter_date)
        
    import os
    import time
    import uuid
    
    unique_id = str(uuid.uuid4())[:8].upper()
    doc_title = f"AGROS_Activity_Report_{unique_id}"
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{doc_title}.pdf"'
    
    # Passing standard name and unique identifier to metadata so it doesn't say "anonymous"
    doc = SimpleDocTemplate(
        response, 
        pagesize=letter,
        title=doc_title,
        author="AGROS System"
    )
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=15,
        alignment=1 # Center
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=20,
        alignment=1,
        textColor=colors.darkgray
    )
    
    # Add Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'agros_logo.png')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=1*28.35, height=1*28.35) # 1x1 inch approximately
        elements.append(img)
        elements.append(Spacer(1, 15))

    elements.append(Paragraph("AGROS - Comprehensive Agricultural Report", title_style))
    
    filter_text = "Filtered by: "
    if estate_id:
        estate = Estate.objects.filter(id=estate_id).first()
        if estate:
            filter_text += f"{estate.estate_name} "
    if plot_id:
        plot = Plot.objects.filter(id=plot_id).first()
        if plot:
            filter_text += f"- Plot: {plot.plot_name}"
    
    if not estate_id and not plot_id:
        filter_text += "Overview (All Estates & Plots)"
        
    elements.append(Paragraph(filter_text, subtitle_style))
    
    # Define generic table style
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

    elements.append(Paragraph("<b>Activity Logs</b>", styles['Heading3']))
    
    act_data = [['Date', 'Estate', 'Plot', 'Category', 'Description']]
    for act in activities[:200]: # Safety limit
        act_data.append([
            act.activity_date.strftime("%b %d, %Y"), 
            Paragraph(act.plot.estate.estate_name, styles['Normal']), 
            Paragraph(act.plot.plot_name, styles['Normal']), 
            Paragraph(act.category.category_name, styles['Normal']),
            Paragraph(act.description or "N/A", styles['Normal'])
        ])
    
    if len(act_data) > 1:
        # Col widths: Date, Estate, Plot, Category, Description
        act_table = Table(act_data, colWidths=[70, 90, 90, 90, 160])
        act_table.setStyle(t_style)
        elements.append(act_table)
    else:
        elements.append(Paragraph("<i>No activities found for this filter.</i>", styles['Normal']))

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<b>Production Output</b>", styles['Heading3']))
    
    prod_data = [['Harvest Date', 'Estate', 'Plot', 'Quantity (kg)']]
    for prod in productions[:200]:
        prod_data.append([
            prod.harvest_date.strftime("%b %d, %Y"), 
            Paragraph(prod.plot.estate.estate_name, styles['Normal']), 
            Paragraph(prod.plot.plot_name, styles['Normal']), 
            f"{prod.quantity} kg"
        ])
        
    if len(prod_data) > 1:
        prod_table = Table(prod_data, colWidths=[100, 120, 120, 100])
        prod_table.setStyle(t_style)
        elements.append(prod_table)
    else:
        elements.append(Paragraph("<i>No production records found for this filter.</i>", styles['Normal']))

    doc.build(elements)
    return response
