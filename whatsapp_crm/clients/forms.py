from django import forms
from .models import Client

class WhatsAppMessageForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Type your WhatsApp message here...',
            'rows': 3
        }),
        label="Message"
    )

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'phone_number', 'email', 'status', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Enter client's full name"
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'client@example.com'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Any relevant notes about this client...',
                'rows': 4
            }),
        }
