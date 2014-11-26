import csv
from django.conf import settings

from django.db import models, connection
from django.utils.timezone import now

from domain.models import CSADataRow


class CellSliderDataRow(CSADataRow, models.Model):
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

    @classmethod
    def ValidateHeaders(cls, data_file):
        with open(data_file.data_file_path, 'r') as f:
            headers = next(f)
            expected_headers = '"id","user_name","image_name","split_number","image_url","has_cancer_count",' \
                               '"has_fiber_count","has_blood_cell_count","amount","proportion","intensity",' \
                               '"created_at"\n'
            if headers != expected_headers:
                raise Exception(
                    "Headers in the CSV file do not match the expected format.\n Expected: %s \n\n But got: %s" % (
                        expected_headers, headers))

    @classmethod
    def ImportFromFile(cls, data_file):
        csa_data_rows = []
        total_row = 0
        with open(data_file.data_file_path, 'r') as f:
            for line in f:
                total_row += 1
        with open(data_file.data_file_path, 'r') as f:
            reader = csv.reader(f)
            x = -1
            for row in reader:
                x += 1
                if x == 0:  # headers
                    continue
                if settings.LIMIT_DATA_IMPORT:
                    if x == settings.LIMIT_DATA_IMPORT:
                        break
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
                if x % 1000 == 0 or x == (total_row - 1):
                    cursor = connection.cursor()
                    statement = "INSERT INTO cellsliderdata_cellsliderdatarow (csa_id, user_name, image_name, split_number, image_url, has_cancer_count, has_fiber_count, has_blood_cell_count, amount, proportion, intensity, csa_created_at, created, updated) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.executemany(statement, csa_data_rows)
                    csa_data_rows = []
                    yield total_row, x
        yield 1, 0.1


