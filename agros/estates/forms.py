from django import forms
from .models import Estate

class EstateForm(forms.ModelForm):
    class Meta:
        model = Estate
        fields = ['estate_name', 'location', 'total_area']
        widgets = {
            'estate_name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'total_area': forms.NumberInput(attrs={'class': 'form-control'}),
        }
