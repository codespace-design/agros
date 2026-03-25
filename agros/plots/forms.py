from django import forms
from .models import Plot

class PlotForm(forms.ModelForm):
    class Meta:
        model = Plot
        fields = ['estate', 'plot_name', 'plant_count']
        widgets = {
            'estate': forms.Select(attrs={'class': 'form-select'}),
            'plot_name': forms.TextInput(attrs={'class': 'form-control'}),
            'plant_count': forms.NumberInput(attrs={'class': 'form-control'}),
        }
