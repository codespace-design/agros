from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from agros.utils import log_action
from .models import Estate
from .forms import EstateForm

def is_admin(user):
    return user.role == 'ADMIN' or user.is_superuser

@login_required
def estate_list(request):
    estates = Estate.objects.all()
    return render(request, 'estates/estate_list.html', {'estates': estates})

@login_required
@user_passes_test(is_admin)
def estate_create(request):
    if request.method == "POST":
        form = EstateForm(request.POST)
        if form.is_valid():
            estate = form.save()
            log_action(request.user, estate, ADDITION, f"Created Estate: {estate.estate_name}")
            messages.success(request, f"Estate '{estate.estate_name}' created successfully.")
            return redirect('estate-list')
    else:
        form = EstateForm()
    return render(request, 'estates/estate_form.html', {'form': form, 'title': 'Add Estate'})

@login_required
@user_passes_test(is_admin)
def estate_update(request, pk):
    estate = get_object_or_404(Estate, pk=pk)
    if request.method == "POST":
        form = EstateForm(request.POST, instance=estate)
        if form.is_valid():
            form.save()
            log_action(request.user, estate, CHANGE, f"Updated Estate: {estate.estate_name}")
            messages.success(request, f"Estate '{estate.estate_name}' updated successfully.")
            return redirect('estate-list')
    else:
        form = EstateForm(instance=estate)
    return render(request, 'estates/estate_form.html', {'form': form, 'title': 'Edit Estate'})

@login_required
@user_passes_test(is_admin)
def estate_delete(request, pk):
    estate = get_object_or_404(Estate, pk=pk)
    if request.method == "POST":
        name = estate.estate_name
        # Log before deletion to have the object properties
        log_action(request.user, estate, DELETION, f"Deleted Estate: {name}")
        estate.delete()
        messages.warning(request, f"Estate '{name}' has been deleted.")
        return redirect('estate-list')
    return render(request, 'estates/estate_confirm_delete.html', {'estate': estate})
