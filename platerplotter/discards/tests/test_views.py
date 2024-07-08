from datetime import datetime, date

import pytz
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from platerplotter.models import HoldingRack, Gel1008Csv, Plate


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testing12345'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        HoldingRack.objects.create(holding_rack_id='tt12345673', discarded=False)

    def _discard_holding_rack(self, rack_id):
        """Helper function to discard a holding rack."""
        return self.client.post(reverse('discards:discards_index'), {
            'holding_rack_id': rack_id,
            'selected_rack': [rack_id],
            'checked_by': 'Test User'
        }, follow=True)

    def test_discards_index_no_items(self):
        response = self.client.get(reverse('discards:discards_index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discards/discard.html')
        self.assertContains(response, 'No holding racks available')

    def test_discards_index_items(self):
        gel1008 = Gel1008Csv.objects.create(filename='ngis_bio_to_gel_sample_dispatch_20240212_093348.csv',
                                            report_generated_datetime=datetime.now(pytz.timezone('UTC')),
                                            date_of_dispatch=datetime(2020, 1, 1, tzinfo=pytz.UTC)
                                            )
        plate = Plate.objects.create(plate_id='LP1234816-DNA', gel_1008_csv=gel1008)
        holding_rack = HoldingRack.objects.create(holding_rack_id='tt12345678', plate=plate)

        response = self.client.get(reverse('discards:discards_index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discards/discard.html')
        self.assertContains(response, holding_rack.holding_rack_id)

    def test_discards_holding_racks(self):
        response = self._discard_holding_rack('tt12345673')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Holding Racks discarded successfully')
        holding_rack = HoldingRack.objects.get(holding_rack_id='tt12345673')
        self.assertEqual(holding_rack.discarded, True)

    def test_discards_query(self):
        self._discard_holding_rack('tt12345673')
        response = self.client.get(reverse('discards:discards_index'), {'q': 'tt12345673'})
        self.assertContains(response, 'Holding Rack has been discarded')

    def test_discarded(self):
        self._discard_holding_rack('tt12345673')
        response = self.client.get(reverse('discards:all_discards_view'))
        self.assertContains(response, 'tt12345673')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discards/all_discards.html')


