from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, SystemSetting

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'status', 'is_active')

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=[('MANAGER', 'Estate Manager'), ('WORKER', 'Labor')])
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'role')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')

class SystemSettingForm(forms.ModelForm):
    class Meta:
        model = SystemSetting
        fields = ('key', 'value', 'description')
        widgets = {
            'key': forms.TextInput(attrs={'readonly': 'readonly'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }
