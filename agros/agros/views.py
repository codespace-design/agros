from django.shortcuts import render, redirect, get_object_or_404
from users.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.models import CHANGE
from agros.utils import log_action
from django.db.models import Sum
from estates.models import Estate
from plots.models import Plot
from labor.models import Labor
from activities.models import Activity, TaskAssignment
from production.models import Production
from labor.models import Payment
from django.utils import timezone

def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')

@login_required
def dashboard(request):
    # Worker Dashboard
    if request.user.role == 'WORKER' and not request.user.is_superuser:
        # Safely attempt to get the connected worker profile
        worker_profile = getattr(request.user, 'worker_profile', None)
        my_tasks = []
        my_attendance = []
        
        if worker_profile:
            my_tasks = TaskAssignment.objects.filter(worker=worker_profile).select_related('plot', 'activity').order_by('-task_date')[:10]
            my_attendance = getattr(worker_profile, 'attendance_records').all().order_by('-date')[:10]
            
        return render(request, 'worker_dashboard.html', {
            'my_tasks': my_tasks,
            'my_attendance': my_attendance,
            'worker_profile': worker_profile
        })

    # Manager Dashboard
    if request.user.role == 'MANAGER':
        recent_activities = Activity.objects.select_related('plot', 'category').order_by('-activity_date')[:5]
        latest_production = Production.objects.select_related('plot').order_by('-harvest_date')[:5]
        recent_tasks = TaskAssignment.objects.select_related('worker', 'activity__category').exclude(status='COMPLETED').order_by('-task_date')[:5]
        
        total_earned = TaskAssignment.objects.filter(status='COMPLETED').aggregate(total=Sum('wage'))['total'] or 0
        total_paid = Payment.objects.filter(worker__isnull=False).aggregate(total=Sum('amount'))['total'] or 0
        total_due = total_earned - total_paid

        manager_stats = {
            'activities_count': Activity.objects.count(),
            'tasks_count': TaskAssignment.objects.filter(status='PENDING').count(),
            'labor_count': Labor.objects.count(),
            'total_due': total_due
        }
        return render(request, 'manager_dashboard.html', {
            'recent_activities': recent_activities, 
            'latest_production': latest_production,
            'recent_tasks': recent_tasks,
            'stats': manager_stats
        })
        
    # Admin Dashboard
    if request.user.role == 'ADMIN' or request.user.is_superuser:
        # Financial Overview
        total_earned = TaskAssignment.objects.filter(status='COMPLETED').aggregate(total=Sum('wage'))['total'] or 0
        total_paid = Payment.objects.filter(worker__isnull=False).aggregate(total=Sum('amount'))['total'] or 0
        global_due = total_earned - total_paid

        # Activity & System Pulse
        recent_activities = Activity.objects.select_related('plot', 'category').order_by('-activity_date')[:5]
        latest_production = Production.objects.select_related('plot').order_by('-harvest_date')[:5]
        recent_tasks = TaskAssignment.objects.select_related('worker', 'activity__category').order_by('-task_date')[:8]
        
        # Verification Queue
        pending_users = User.objects.filter(is_active=False).order_by('-date_joined')
        
        stats = {
            'estates_count': Estate.objects.count(),
            'plots_count': Plot.objects.count(),
            'labor_count': Labor.objects.count(),
            'total_production': Production.objects.aggregate(total=Sum('quantity'))['total'] or 0,
            'global_due': global_due,
            'pending_approval_count': pending_users.count()
        }
        
        from django.contrib.admin.models import LogEntry
        
        # Access Logs (Logins/Logouts)
        access_logs = LogEntry.objects.filter(change_message__in=["Logged In (Manager)", "Logged In (Worker)", "Logged Out (Manager)", "Logged Out (Worker)"]).select_related('user').order_by('-action_time')[:10]
        
        context = {
            'stats': stats,
            'recent_activities': recent_activities,
            'latest_production': latest_production,
            'recent_tasks': recent_tasks,
            'pending_users': pending_users,
            'access_logs': access_logs
        }
        return render(request, 'dashboard.html', context)

    # Fallback for unexpected roles
    return redirect('landing')

@login_required
def mark_task_complete(request, task_id):
    if request.method == "POST" and (request.user.role in ['ADMIN', 'MANAGER'] or request.user.is_superuser):
        task = get_object_or_404(TaskAssignment, id=task_id)
        if task.status != 'COMPLETED':
            task.status = 'COMPLETED'
            task.completed_at = timezone.now()
            task.save()
            log_action(request.user, task, CHANGE, f"Marked Task Complete for {task.worker.name}")
            messages.success(request, f"Task marked as completed.")
    
    # Redirect back to where the request came from (Task List or Dashboard)
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

