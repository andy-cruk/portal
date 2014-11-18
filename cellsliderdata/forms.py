import re
from django import forms

re_csa_zip_file_name = re.compile(r'^\d{4}-\d{2}-\d{2}_cancer_cells_classifications\.csv\.tar\.gz$')


class CSAZipFileForm(forms.Form):
    zip_file = forms.FileField(
        label="Click the browse button below to select the file sent to you by the CSA",
        help_text="The file must be in .tar.gz format and the name should look almost exactly like this: "
                  "2014-11-02_cancer_cells_classifications.csv.tar.gz (but with the right year-month-date of cause!)"
    )

    def clean_zip_file(self):
        zip_file = self.cleaned_data.get('zip_file')
        if not zip_file:
            raise forms.ValidationError('You must select a file to upload')
        if not re_csa_zip_file_name.search(zip_file.name):
            raise forms.ValidationError(
                'The name of this file does seem right. Files must be named like this '
                '2014-11-02_cancer_cells_classifications.csv.tar.gz (but with the right year-month-date of cause!)')
        return zip_file