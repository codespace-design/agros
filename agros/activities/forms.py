from django import forms
from .models import ActivityCategory, Activity, TaskAssignment
from labor.models import Labor

class ActivityCategoryForm(forms.ModelForm):
    class Meta:
        model = ActivityCategory
        fields = ['category_name', 'description']
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ActivityForm(forms.ModelForm):
    workers = forms.ModelMultipleChoiceField(
        queryset=Labor.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        help_text="Select one or more workers to assign to this activity."
    )
    wage_per_worker = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 500.00'})
    )

    class Meta:
        model = Activity
        fields = ['plot', 'category', 'activity_date', 'description', 'workers', 'wage_per_worker']
        widgets = {
            'plot': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'activity_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class TaskAssignmentForm(forms.ModelForm):
    class Meta:
        model = TaskAssignment
        fields = ['worker', 'plot', 'activity', 'task_date', 'wage', 'status']
        widgets = {
            'worker': forms.Select(attrs={'class': 'form-select'}),
            'plot': forms.Select(attrs={'class': 'form-select'}),
            'activity': forms.Select(attrs={'class': 'form-select'}),
            'task_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'wage': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
