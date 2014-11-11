import json
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.test import TestCase
from django.core.urlresolvers import reverse
from cellsliderdata.models import Classification, Image, ImageSplit, CitizenScientists


class ClassificationTestCase(TestCase):
    def test_from_data(self):
        """Can a classification and dependant objects be built from data"""
        data = {
            'amount': '',
            'created_at': '2012-10-23 17:39:42 UTC',
            'has_blood_cell_count': '',
            'has_cancer_count': '',
            'has_fiber_count': '',
            'id': '5086d65e56175a680800012d',
            'image_name': 'BCAC/ER/DIAC_1/DIAC_1_0_12_1.tiff',
            'image_url': 'http://www.cellslider.net/cells/5085ca86ea3052329e00b1aa.jpg',
            'intensity': '',
            'proportion': '',
            'split_number': '13',
            'user_name': 'stuart.lynn'}
        classification = Classification.FromData(data)
        self.assertTrue(Classification.objects.filter(id=classification.id).count() == 1)
        images = Image.objects.filter(name=data['image_name'])
        self.assertTrue(images.count() == 1)
        self.assertTrue(ImageSplit.objects.filter(image=images[0], split=data['split_number']).count() == 1)
        self.assertTrue(CitizenScientists.objects.filter(user_name=data['user_name']).count() == 1)
        classification = Classification.FromData(data)


class APIViewTests(TestCase):
    def test_api_add_cell_slider_data(self):
        url = reverse('cell_slider_data_api_add_data')

        # no get
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

        # no api_key
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 403)

        # bad api_key
        response = self.client.post(url, {'api_key': 'jhdjfhjdf'})
        self.assertEqual(response.status_code, 403)

        # no data
        response = self.client.post(url, {'api_key': settings.CELL_SLIDER_DATA_API_KEY})
        self.assertEqual(response.status_code, HttpResponseBadRequest.status_code)

        # bad data
        response = self.client.post(url, {'api_key': settings.CELL_SLIDER_DATA_API_KEY, 'data': 'jhfjdhfjd'})
        self.assertEqual(response.status_code, HttpResponseBadRequest.status_code)

        # empty data
        response = self.client.post(url, {'api_key': settings.CELL_SLIDER_DATA_API_KEY, 'data': '[]'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['processed'], 0)

        # bad data - no id
        response = self.client.post(url, {'api_key': settings.CELL_SLIDER_DATA_API_KEY, 'data': '[{"foo":"bar"}]'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['processed'], 0)
        self.assertEqual(data['rejected']['count'], 1)
        self.assertEqual(len(data['rejected']['errors']), 0)

        # bad data - with id
        response = self.client.post(url, {'api_key': settings.CELL_SLIDER_DATA_API_KEY, 'data': '[{"id":"bar"}]'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['processed'], 0)
        self.assertEqual(data['rejected']['count'], 1)
        self.assertEqual(len(data['rejected']['errors'].keys()), 1)
        self.assertEqual(data['rejected']['errors']['bar'], "'image_name' (<class 'KeyError'>)")



