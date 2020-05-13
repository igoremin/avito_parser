from django import forms
from .models import ProxyIP


class ProxyIPForm(forms.ModelForm):
    class Meta:
        model = ProxyIP
        fields = ['ip', 'port', 'login', 'password']

        field_classes = {
            'ip': forms.CharField,
            'port': forms.CharField,
            'login': forms.CharField,
            'password': forms.CharField,
        }

        widgets = {
            'ip': forms.TextInput(attrs={'class': 'form-control'}),
            'port': forms.TextInput(attrs={'class': 'form-control'}),
            'login': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.TextInput(attrs={'class': 'form-control'}),
        }
