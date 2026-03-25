from django import forms
from .models import Labor, Attendance, Payment
from django.contrib.auth import get_user_model

User = get_user_model()

class LaborForm(forms.ModelForm):
    class Meta:
        model = Labor
        fields = ['user', 'name', 'phone', 'address']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'type': 'tel', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show WORKER users who don't have a profile yet (or are already linked to THIS profile)
        linked_users = Labor.objects.exclude(user__isnull=True).values_list('user_id', flat=True)
        if self.instance and self.instance.user_id:
            # If editing, allow keeping the current user
            linked_users = linked_users.exclude(user_id=self.instance.user_id)
        
        self.fields['user'].queryset = User.objects.filter(role='WORKER').exclude(id__in=linked_users)
        self.fields['user'].required = False
        self.fields['user'].label = "Linked Login Account"

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['worker', 'date', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'worker': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['worker', 'amount', 'date', 'notes']
        widgets = {
            'worker': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes'].required = False
        self.fields['notes'].label = "Description / Notes (Optional)"

class ManagerPaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['manager', 'amount', 'date', 'notes']
        widgets = {
            'manager': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manager'].queryset = User.objects.filter(role='MANAGER')
        self.fields['manager'].label = "Estate Manager"
