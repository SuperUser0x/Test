from django import forms

class WhatsAppMessageForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        label="Message"
    )
