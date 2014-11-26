import csv
from django.conf import settings
from django.db import models, connection
from domain.models import CSADataRow


class RTODataRow(CSADataRow, models.Model):
    csa_id = models.CharField(max_length=255)
    activated_at = models.DateTimeField()
    created_at = models.DateTimeField()
    classification_count = models.IntegerField(blank=True, null=True)
    q1a1 = models.IntegerField(blank=True, null=True)
    q1a2 = models.IntegerField(blank=True, null=True)
    q2a0 = models.IntegerField(blank=True, null=True)
    q2a1 = models.IntegerField(blank=True, null=True)
    q2a2 = models.IntegerField(blank=True, null=True)
    q2a3 = models.IntegerField(blank=True, null=True)
    q2a4 = models.IntegerField(blank=True, null=True)
    q2a5 = models.IntegerField(blank=True, null=True)
    q2a6 = models.IntegerField(blank=True, null=True)
    q3a0 = models.IntegerField(blank=True, null=True)
    q3a1 = models.IntegerField(blank=True, null=True)
    q3a2 = models.IntegerField(blank=True, null=True)
    q3a3 = models.IntegerField(blank=True, null=True)
    q3a4 = models.IntegerField(blank=True, null=True)
    metadata_index = models.IntegerField(blank=True, null=True)
    metadata_collection = models.CharField(max_length=255)
    metadata_id_number = models.CharField(max_length=255)
    metadata_stain_type = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    original_file_name = models.CharField(max_length=2055)
    random = models.CharField(max_length=255)
    updated_at = models.DateTimeField()
    zooniverse_id = models.CharField(max_length=255)

    @classmethod
    def ValidateHeaders(cls, data_file):
        return True
    
    @classmethod
    def ImportFromFile(cls, data_file):
        csa_data_rows = []
        total_row = 0
        with open(data_file.data_file_path, 'r') as f:
            for line in f:
                total_row += 1
        with open(data_file.data_file_path, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
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
                    row[3],
                    row[2],
                    row[10],
                    row[11],
                    row[12],
                    row[13],
                    row[14],
                    row[15],
                    row[16],
                    row[17],
                    row[18],
                    row[19],
                    row[20],
                    row[21],
                    row[22],
                    row[23],
                    row[28],
                    row[26],
                    row[27],
                    row[31],
                    row[34],
                    row[30],
                    row[33],
                    row[35],
                    row[37],))
                if x % 1000 == 0 or x == (total_row - 1):
                    cursor = connection.cursor()
                    statement = "INSERT INTO rtodata_rtodatarow (csa_id, activated_at, created_at, classification_count, q1a1, q1a2, q2a0, q2a1, q2a2, q2a3, q2a4, q2a5, q2a6, q3a0, q3a1, q3a2, q3a3, q3a4, metadata_index, metadata_collection, metadata_id_number, metadata_stain_type, state, original_file_name, random, updated_at, zooniverse_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.executemany(statement, csa_data_rows)
                    csa_data_rows = []
                    yield total_row, x
        yield 1, 0.1

