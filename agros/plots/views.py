from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from agros.utils import log_action
from .models import Plot
from .forms import PlotForm

def is_manager_or_admin(user):
    return user.role in ['ADMIN', 'MANAGER'] or user.is_superuser

@login_required
def plot_list(request):
    plots = Plot.objects.select_related('estate').all()
    return render(request, 'plots/plot_list.html', {'plots': plots})

@login_required
@user_passes_test(is_manager_or_admin)
def plot_create(request):
    if request.method == "POST":
        form = PlotForm(request.POST)
        if form.is_valid():
            plot = form.save()
            log_action(request.user, plot, ADDITION, f"Added Plot: {plot.plot_name}")
            messages.success(request, f"Plot '{plot.plot_name}' added successfully.")
            return redirect('plot-list')
    else:
        form = PlotForm()
    return render(request, 'plots/plot_form.html', {'form': form, 'title': 'Add Plot'})

@login_required
@user_passes_test(is_manager_or_admin)
def plot_update(request, pk):
    plot = get_object_or_404(Plot, pk=pk)
    if request.method == "POST":
        form = PlotForm(request.POST, instance=plot)
        if form.is_valid():
            form.save()
            log_action(request.user, plot, CHANGE, f"Updated Plot: {plot.plot_name}")
            messages.success(request, f"Plot '{plot.plot_name}' updated successfully.")
            return redirect('plot-list')
    else:
        form = PlotForm(instance=plot)
    return render(request, 'plots/plot_form.html', {'form': form, 'title': 'Edit Plot'})

@login_required
@user_passes_test(is_manager_or_admin)
def plot_delete(request, pk):
    plot = get_object_or_404(Plot, pk=pk)
    if request.method == "POST":
        name = plot.plot_name
        log_action(request.user, plot, DELETION, f"Deleted Plot: {name}")
        plot.delete()
        messages.warning(request, f"Plot '{name}' has been deleted.")
        return redirect('plot-list')
    return render(request, 'plots/plot_confirm_delete.html', {'plot': plot})
