from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.admin.models import ADDITION
from agros.utils import log_action
from .models import ActivityCategory, Activity, TaskAssignment
from .forms import ActivityCategoryForm, ActivityForm, TaskAssignmentForm

def is_admin(user):
    return user.role == 'ADMIN' or user.is_superuser

def is_manager_or_admin(user):
    return user.role in ['ADMIN', 'MANAGER'] or user.is_superuser

# Category Views
@login_required
def category_list(request):
    categories = ActivityCategory.objects.all()
    return render(request, 'activities/category_list.html', {'categories': categories})

@login_required
@user_passes_test(is_manager_or_admin)
def category_create(request):
    if request.method == "POST":
        form = ActivityCategoryForm(request.POST)
        if form.is_valid():
            cat = form.save()
            log_action(request.user, cat, ADDITION, f"Added Activity Category: {cat.category_name}")
            messages.success(request, f"Category '{cat.category_name}' added successfully.")
            return redirect('category-list')
    else:
        form = ActivityCategoryForm()
    return render(request, 'activities/category_form.html', {'form': form, 'title': 'Add Activity Category'})

# Activity Views
@login_required
def activity_list(request):
    activities = Activity.objects.select_related('plot', 'category').all()
    return render(request, 'activities/activity_list.html', {'activities': activities})

@login_required
@user_passes_test(is_manager_or_admin)
def activity_create(request):
    if request.method == "POST":
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save()
            log_action(request.user, activity, ADDITION, f"Recorded Activity on {activity.plot.plot_name}")
            
            # Sub-routing: If the Manager selected workers while creating the Activity, assign them immediately.
            workers = form.cleaned_data.get('workers')
            wage = form.cleaned_data.get('wage_per_worker') or 0.00
            
            if workers:
                for worker in workers:
                    assignment = TaskAssignment.objects.create(
                        worker=worker,
                        plot=activity.plot,
                        activity=activity,
                        task_date=activity.activity_date,
                        wage=wage,
                        status='PENDING'
                    )
                    log_action(request.user, assignment, ADDITION, f"Assigned Task to {worker.name}")
                messages.success(request, f"Activity recorded and {workers.count()} workers assigned.")
            else:
                messages.success(request, "Activity recorded successfully without active assignments.")
                    
            return redirect('activity-list')
    else:
        form = ActivityForm()
    return render(request, 'activities/activity_form.html', {'form': form, 'title': 'Record Activity'})

# Task Assignment Views
@login_required
def task_list(request):
    assignments = TaskAssignment.objects.select_related('worker', 'plot', 'activity').all()
    return render(request, 'activities/task_list.html', {'assignments': assignments})

@login_required
@user_passes_test(is_manager_or_admin)
def task_assign(request):
    if request.method == "POST":
        form = TaskAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save()
            log_action(request.user, assignment, ADDITION, f"Assigned Task to {assignment.worker.name}")
            messages.success(request, f"Task successfully assigned to {assignment.worker.name}.")
            return redirect('task-list')
    else:
        form = TaskAssignmentForm()
    return render(request, 'activities/task_form.html', {'form': form, 'title': 'Assign Task'})
