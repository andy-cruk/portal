from django import forms


class CSAZipFileForm(forms.Form):
    zip_file = forms.FileField()