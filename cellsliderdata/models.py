from django.db import models


class CSAZipFile(models.Model):
    original_file_name = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    upload = models.FileField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @classmethod
    def Create(cls, zip_file):
        csa_zip_file, created = CSAZipFile.objects.get_or_create(
            original_file_name=zip_file.name,
            defaults={
                'name': zip_file.name,
                'upload': zip_file})
        return csa_zip_file


