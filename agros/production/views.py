from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.admin.models import ADDITION
from agros.utils import log_action
from .models import Production
from .forms import ProductionForm

def is_manager_or_admin(user):
    return user.role in ['ADMIN', 'MANAGER'] or user.is_superuser

@login_required
def production_list(request):
    productions = Production.objects.select_related('plot').all()
    return render(request, 'production/production_list.html', {'productions': productions})

@login_required
@user_passes_test(is_manager_or_admin)
def production_create(request):
    if request.method == "POST":
        form = ProductionForm(request.POST)
        if form.is_valid():
            prod = form.save()
            log_action(request.user, prod, ADDITION, f"Recorded Production: {prod.quantity}kg")
            messages.success(request, f"Production of {prod.quantity}kg recorded for {prod.plot.plot_name}.")
            return redirect('production-list')
    else:
        form = ProductionForm()
    return render(request, 'production/production_form.html', {'form': form, 'title': 'Record Production'})
