import os
import re
import csv
import tarfile
from django.conf import settings
from django.core.cache import cache
from django.db import models, connection
from django.utils.timezone import now


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

    def validate_headers(self):
        with open(self.data_file_path, 'r') as f:
            headers = next(f)
            expected_headers = '"id","user_name","image_name","split_number","image_url","has_cancer_count",' \
                               '"has_fiber_count","has_blood_cell_count","amount","proportion","intensity",' \
                               '"created_at"\n'
            if headers != expected_headers:
                raise Exception(
                    "Headers in the CSV file do not match the expected format.\n Expected: %s \n\n But got: %s" % (
                        expected_headers, headers))

    def import_from_file(self):
        csa_data_rows = []
        total_row = 0
        with open(self.data_file_path, 'r') as f:
            for line in f:
                total_row += 1
        with open(self.data_file_path, 'r') as f:
            reader = csv.reader(f)
            x = -1
            for row in reader:
                x += 1
                if x == 0:  # headers
                    continue
                # if x > 100000:
                #     break
                if x % 1000 == 0:
                    cursor = connection.cursor()
                    statement = "INSERT INTO cellsliderdata_csadatarow (csa_id, user_name, image_name, split_number, image_url, has_cancer_count, has_fiber_count, has_blood_cell_count, amount, proportion, intensity, csa_created_at, created, updated) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.executemany(statement, csa_data_rows)
                    csa_data_rows = []
                    yield total_row, x
                csa_data_rows.append((
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    1 if row[5] == '1' else 0,
                    1 if row[6] == '1' else 0,
                    1 if row[7] == '1' else 0,
                    row[8],
                    row[9],
                    row[10],
                    row[11].replace(' UTC', '+00:00').replace(' ', 'T').strip(),
                    now().isoformat(),
                    now().isoformat()))
        yield 1, 0.1


class CSADataRow(models.Model):
    csa_id = models.CharField(max_length=255)
    user_name = models.CharField(max_length=1023)
    image_name = models.CharField(max_length=1023)
    split_number = models.CharField(max_length=255)
    image_url = models.CharField(max_length=1023)
    has_cancer_count = models.BooleanField(default=False)
    has_fiber_count = models.BooleanField(default=False)
    has_blood_cell_count = models.BooleanField(default=False)
    amount = models.CharField(max_length=255)
    proportion = models.CharField(max_length=255)
    intensity = models.CharField(max_length=255)
    csa_created_at = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


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
    def RunProcessForZipFile(cls, csa_zip_file):
        process, created = CSAZipFileProcess.objects.get_or_create(csa_zip_file=csa_zip_file)
        process.run()

    def _set_state(self, state, error=None, exception=None, import_progress=None):
        self.state = state
        if error:
            self.error = error
        if exception:
            self.exception = exception
        if import_progress:
            self.data_import_progress = import_progress
        self.save()

    def run(self):
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
            self.csa_data_file.validate_headers()
            self._set_state(CSAZipFileProcess.STATE_IMPORTING)
        except Exception as ex:
            self._set_state(
                CSAZipFileProcess.STATE_ERROR,
                "There was an error validating the headers in the Zip File.",
                ex)
            return

        # Import the data
        try:
            CSADataRow.objects.all().delete()
            for total, done in self.csa_data_file.import_from_file():
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
