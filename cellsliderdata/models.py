from django.db import models


class Image(models.Model):
    name = models.CharField(max_length=1023)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class ImageSplit(models.Model):
    image = models.ForeignKey(Image)
    url = models.CharField(max_length=1023)
    split = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class CitizenScientists(models.Model):
    user_name = models.CharField(max_length=1023)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Classification(models.Model):
    cell_slider_id = models.CharField(max_length=255, unique=True)
    image_split = models.ForeignKey(ImageSplit)
    citizen_scientist = models.ForeignKey(CitizenScientists)
    has_cancer_count = models.BooleanField(default=False)
    has_fiber_count = models.BooleanField(default=False)
    has_blood_cell_count = models.BooleanField(default=False)
    amount = models.CharField(max_length=255, null=True, blank=True)
    proportion = models.IntegerField(null=True, blank=True)
    intensity = models.CharField(max_length=255, null=True, blank=True)
    cell_slider_created_at = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @classmethod
    def FromData(cls, data):
        image, created = Image.objects.get_or_create(name=data['image_name'])
        image_split, created = ImageSplit.objects.get_or_create(image=image, url=data['image_url'], split=data['split_number'])
        citizen_scientist, created = CitizenScientists.objects.get_or_create(user_name=data['user_name'])
        classification, created = Classification.objects.get_or_create(
            cell_slider_id=data['id'],
            defaults={
                'image_split': image_split,
                'citizen_scientist': citizen_scientist,
                'has_cancer_count': data['has_cancer_count'] == '1',
                'has_fiber_count': data['has_fiber_count'] == '1',
                'has_blood_cell_count': data['has_blood_cell_count'] == '1',
                'amount': data['amount'] or None,
                'proportion': int(data['proportion'].replace('%', '')) if data['proportion'] and data['proportion'] != 'none' else None,
                'intensity': data['intensity'] or None,
                'cell_slider_created_at': data['created_at'].replace('UTC', '').strip(),
            })
        return classification




