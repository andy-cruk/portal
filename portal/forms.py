from django import forms
from django.contrib.auth.models import User


class PortalLoginForm(forms.Form):
    next = forms.CharField(widget=forms.HiddenInput, required=False)
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'addon_after': '<i class="fa fa-envelope"></i>'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'addon_after': '<i class="fa fa-key"></i>'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PortalLoginForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = super(PortalLoginForm, self).clean().get('email')
        if not User.objects.filter(email=email).count():
            raise forms.ValidationError('This email address is not registered')
        return email