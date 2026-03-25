from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login, logout, update_session_auth_hash, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from agros.utils import log_action
from .models import User, SystemSetting
from .forms import CustomUserCreationForm, CustomUserChangeForm, SignupForm, UserProfileForm, SystemSettingForm

def is_admin(user):
    return user.role == 'ADMIN' or user.is_superuser

@login_required
@user_passes_test(is_admin)
def settings_manage(request):
    if not SystemSetting.objects.exists():
        defaults = [
            ("BASE_WAGE", "550", "Default daily wage for workers"),
            ("WORKING_HOURS", "8", "Standard default working hours"),
            ("OVERTIME_MULTIPLIER", "1.5", "Multiplier for overtime pay"),
            ("COMPANY_NAME", "GreenCardamom Estates", "Official organizational name"),
        ]
        for key, val, desc in defaults:
            SystemSetting.objects.create(key=key, value=val, description=desc)

    settings = SystemSetting.objects.all()
    if request.method == 'POST':
        for setting in settings:
            new_value = request.POST.get(f'setting_{setting.id}')
            if new_value is not None and setting.value != new_value:
                setting.value = new_value
                setting.save()
                log_action(request.user, setting, CHANGE, f"Updated setting {setting.key} to {new_value}")
        messages.success(request, "System settings updated successfully.")
        return redirect('settings-manage')
    
    return render(request, 'users/system_settings.html', {'settings': settings})

@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all()
    return render(request, 'users/user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def user_create(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_action(request.user, user, ADDITION, f"Created User: {user.username}")
            messages.success(request, f"User '{user.username}' created successfully.")
            return redirect('user-list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/user_form.html', {'form': form, 'title': 'Add User'})

@login_required
@user_passes_test(is_admin)
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            log_action(request.user, user, CHANGE, f"Updated User: {user.username}")
            messages.success(request, f"User {user.username} updated successfully.")
            return redirect('user-list')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'users/user_form.html', {'form': form, 'title': 'Edit User'})

@login_required
@user_passes_test(is_admin)
def user_approve(request, pk):
    if request.method == "POST":
        user_to_approve = get_object_or_404(User, pk=pk)
        user_to_approve.is_active = True
        user_to_approve.status = True
        user_to_approve.save()
        log_action(request.user, user_to_approve, CHANGE, f"Approved User: {user_to_approve.username}")
        
        # Auto-create Labor profile for Labor role if it doesn't exist
        if user_to_approve.role == 'WORKER':
            from labor.models import Labor
            if not Labor.objects.filter(user=user_to_approve).exists():
                labor = Labor.objects.create(
                    user=user_to_approve,
                    name=user_to_approve.get_full_name() or user_to_approve.username,
                    phone="Pending",
                    address="Pending"
                )
                log_action(request.user, labor, ADDITION, f"Auto-generated Labor profile for {user_to_approve.username}")
                messages.info(request, f"Generated Labor profile for {user_to_approve.username}.")

        messages.success(request, f"Account for {user_to_approve.username} ({user_to_approve.get_role_display()}) has been approved and activated.")
    return redirect('user-list')

def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until admin approval
            user.status = False
            user.save()
            
            if user.role == 'MANAGER':
                messages.info(request, "Your Manager account has been created. You will be able to log in once it is approved by an administrator.")
            else:
                messages.info(request, "Your account has been created and is awaiting administrator approval.")
                
            return redirect('landing')
        else:
            # If the form is invalid, grab the errors and push them to the landing page as an alert
            for field, errors in form.errors.items():
                for error in errors:
                    # Map internal field names to friendly names
                    friendly_name = field.replace('password1', 'Password').replace('password2', 'Confirm Password').title()
                    if field == '__all__': friendly_name = 'Error'
                    messages.error(request, f"{friendly_name}: {error}")
            return redirect('landing')
            
    return redirect('landing')

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == "POST":
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        
        user = authenticate(request, username=u_name, password=p_word)
        if user is not None:
            auth_login(request, user)
            if user.role in ['MANAGER', 'WORKER']:
                log_action(user, user, CHANGE, f"Logged In ({user.get_role_display()})")
            return redirect('dashboard')
        else:
            # Login failed. Check if user exists but isn't active
            try:
                existing_user = User.objects.get(username=u_name)
                if not existing_user.is_active:
                    return render(request, 'landing.html', {
                        'login_error': "Your account is pending administrator approval. You cannot log in yet.",
                        'show_login': True,
                        're_username': u_name
                    })
                else:
                    return render(request, 'landing.html', {
                        'login_error': "Invalid username or password.",
                        'show_login': True,
                        're_username': u_name
                    })
            except User.DoesNotExist:
                return render(request, 'landing.html', {
                    'login_error': "Invalid username or password.",
                    'show_login': True,
                    're_username': u_name
                })
                
    return render(request, 'landing.html')

def logout_view(request):
    if request.user.is_authenticated and request.user.role in ['MANAGER', 'WORKER']:
        log_action(request.user, request.user, CHANGE, f"Logged Out ({request.user.get_role_display()})")
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('landing')

@login_required
def profile(request):
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            p_form = UserProfileForm(request.POST, instance=request.user)
            c_form = PasswordChangeForm(request.user)
            if p_form.is_valid():
                p_form.save()
                messages.success(request, 'Your profile has been updated!')
                return redirect('profile')
        elif 'update_password' in request.POST:
            p_form = UserProfileForm(instance=request.user)
            c_form = PasswordChangeForm(request.user, request.POST)
            if c_form.is_valid():
                user = c_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('profile')
    else:
        p_form = UserProfileForm(instance=request.user)
        c_form = PasswordChangeForm(request.user)
        
    context = {
        'p_form': p_form,
        'c_form': c_form
    }
    return render(request, 'users/profile.html', context)
from django.contrib.admin.models import LogEntry

@login_required
@user_passes_test(is_admin)
def activity_log(request):
    logs = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:100]
    return render(request, 'users/activity_log.html', {'logs': logs})
