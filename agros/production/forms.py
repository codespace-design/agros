from django import forms
from .models import Production

class ProductionForm(forms.ModelForm):
    class Meta:
        model = Production
        fields = ['plot', 'harvest_date', 'quantity']
        widgets = {
            'plot': forms.Select(attrs={'class': 'form-select'}),
            'harvest_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
