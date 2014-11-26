import abc
import os
import re
import tarfile
from django.conf import settings
from django.core.cache import cache
from django.db import models


class CSAZipFile(models.Model):
    original_file_name = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    upload = models.FileField(blank=False, null=False)
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


class CSADataFile(models.Model):
    original_file_name = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    data_file_path = models.CharField(max_length=1024)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @classmethod
    def Create(cls, data_file_path):
        data_file_name = data_file_path.split(os.pathsep)[-1]
        csa_zip_file, created = CSADataFile.objects.get_or_create(
            original_file_name=data_file_name,
            defaults={
                'name': data_file_name,
                'data_file_path': data_file_path})
        if not created:
            csa_zip_file.save()  # record that we are using this at this time
        return csa_zip_file

    def validate_headers(self, data_row):
        return data_row.ValidateHeaders(self)

    def import_from_file(self, data_row):
        return data_row.ImportFromFile(self)


class CSADataRow(object):

    def ValidateHeaders(cls, data_file):
        raise NotImplementedError('Must be implemented on instance class')

    def ImportFromFile(cls, data_file):
        raise NotImplementedError('Must be implemented on instance class')


class CSAZipFileProcess(models.Model):
    STATE_ERROR = '00'
    STATE_START = '01'
    STATE_UNZIPPED = '02'
    STATE_CSV_FILE_EXISTS = '03'
    STATE_IMPORTING = '04'
    STATE_FINISHED = '05'

    csa_zip_file = models.ForeignKey(CSAZipFile)
    csa_data_file = models.ForeignKey(CSADataFile, null=True, blank=True)
    state = models.CharField(max_length=2, default=STATE_START)
    error = models.CharField(max_length=255, null=True, blank=True)
    exception = models.TextField(null=True, blank=True)
    data_import_progress = models.FloatField(null=True, blank=True, default=0)

    @classmethod
    def RunProcessForZipFile(cls, csa_zip_file, data_row_class):
        process, created = CSAZipFileProcess.objects.get_or_create(csa_zip_file=csa_zip_file)
        process.run(data_row_class)

    def _set_state(self, state, error=None, exception=None, import_progress=None):
        self.state = state
        if error:
            self.error = error
        if exception:
            self.exception = "%s (%s)" % (exception, type(exception))
        if import_progress:
            self.data_import_progress = import_progress
        self.save()

    def run(self, data_row_class):
        self._set_state(CSAZipFileProcess.STATE_START)

        # Try to extract the zip file
        try:
            tar_file = tarfile.open(os.path.join(settings.MEDIA_ROOT, self.csa_zip_file.name))
            tar_file.extractall(path=settings.MEDIA_ROOT)
            tar_file.close()
            self._set_state(CSAZipFileProcess.STATE_UNZIPPED)
        except Exception as ex:
            self._set_state(
                CSAZipFileProcess.STATE_ERROR,
                "There was an error unzipping the tar file, the file may be corrupt?",
                ex)
            return

        # Try to associate a CSADataFile object with this process
        csa_data_file_name = re.sub(r'\.tar.*', '', self.csa_zip_file.name)
        try:
            data_file_path = os.path.join(settings.MEDIA_ROOT, csa_data_file_name)
            csa_data_file = CSADataFile.Create(data_file_path)
            self.csa_data_file = csa_data_file
            self.save()
            self._set_state(CSAZipFileProcess.STATE_CSV_FILE_EXISTS)
        except Exception as ex:
            self._set_state(
                CSAZipFileProcess.STATE_ERROR,
                "There was an error reading the unzipped CSA file.",
                ex)
            return

        # do the headers validate
        try:
            self.csa_data_file.validate_headers(data_row_class)
            self._set_state(CSAZipFileProcess.STATE_IMPORTING)
        except Exception as ex:
            self._set_state(
                CSAZipFileProcess.STATE_ERROR,
                "There was an error validating the headers in the Zip File.",
                ex)
            return

        # Import the data
        try:
            data_row_class.objects.all().delete()
            for total, done in self.csa_data_file.import_from_file(data_row_class):
                self._set_state(CSAZipFileProcess.STATE_IMPORTING, import_progress=float(done)/total * 100)
            self._set_state(CSAZipFileProcess.STATE_FINISHED)
        except Exception as ex:
            self._set_state(
                CSAZipFileProcess.STATE_ERROR,
                "There was an error importing data from the Zip File.",
                ex)
            return

        # Clear the cache of analysis
        cache.clear()

    def get_csa_zip_file_process(self):
        if self.state == CSAZipFileProcess.STATE_START:
            state = 'processing'
            template_data = {
                'progress': 10, 'steps_done': ['Uploaded file'], 'steps_doing': ['Unzipping uploaded file'],
                'steps_todo': ['Loading CSV file', 'Validate file format', 'Import file data']}
        elif self.state == CSAZipFileProcess.STATE_UNZIPPED:
            state = 'processing'
            template_data = {
                'progress': 30, 'steps_done': ['Uploaded file', 'Unzipped uploaded file'],
                'steps_doing': ['Loading CSV file'], 'steps_todo': ['Validating file format', 'Import file data']}
        elif self.state == CSAZipFileProcess.STATE_CSV_FILE_EXISTS:
            state = 'processing'
            template_data = {'progress': 40, 'steps_done': ['Uploaded file', 'Unzipped uploaded file', 'Loading CSV file'],
                             'steps_doing': ['Validating file format'], 'steps_todo': ['Import file data']}
        elif self.state == CSAZipFileProcess.STATE_IMPORTING:
            state = 'processing'
            template_data = {
                'progress': self.data_import_progress,
                'steps_done': [
                    'Uploaded file',
                    'Unzipped uploaded file',
                    'Loading CSV file',
                    'Validating file format'],
                'steps_doing': ['Import file data'],
                'steps_todo': []}
        elif self.state == CSAZipFileProcess.STATE_FINISHED:
            state = 'finished'
            template_data = {
                'progress': 100,
                'steps_done': [
                    'Uploaded file',
                    'Unzipped uploaded file',
                    'Loading CSV file',
                    'Validating file format',
                    'Import file data'],
                'steps_doing': [],
                'steps_todo': []}
        else:  # self.state == CSAZipFileProcess.STATE_ERROR:
            state = 'error'
            template_data = {'self': self}
        return state, template_data
