from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


class PortalLoginForm(forms.Form):
    next = forms.CharField(widget=forms.HiddenInput, required=False)
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'addon_after': '<i class="fa fa-envelope"></i>'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'addon_after': '<i class="fa fa-key"></i>'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = None
        super(PortalLoginForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = super(PortalLoginForm, self).clean().get('email')
        if not User.objects.filter(email=email).count():
            raise forms.ValidationError('This email address is not registered')
        return email

    def clean_password(self):
        clean_data = super(PortalLoginForm, self).clean()
        email = clean_data.get('email')
        password = clean_data.get('password')
        if email:  # only do this if the email was valid
            self.user = authenticate(username=email, password=password)  # store the user for later login
            if not self.user:
                raise forms.ValidationError('Email and password do not match')
        else:
            raise forms.ValidationError('')
        return password

    def clean(self):
        data = super(PortalLoginForm, self).clean()
        if self.user:  # if the email and password led to a valid user
            if self.user.is_active:
                login(self.request, self.user)
            else:
                raise forms.ValidationError('Your user account is not active')
        return data