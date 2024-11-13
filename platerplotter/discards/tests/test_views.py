from datetime import datetime, date

import pytz
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from platerplotter.models import HoldingRack, Gel1008Csv, Plate, Gel1004Csv, ReceivingRack, Sample, Gel1005Csv, \
    HoldingRackWell


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testing12345'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        self.holding_rack_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        self.holding_rack_columns = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        gel_1005_csv = Gel1005Csv.objects.create(filename='test1005.csv',
                                                 report_generated_datetime=datetime.now(pytz.timezone('UTC')))
        gel_1004_csv = Gel1004Csv.objects.create(filename='test1004.csv', gel_1005_csv=gel_1005_csv,
                                                 plating_organisation='wwm',
                                                 report_received_datetime=datetime.now(pytz.timezone('UTC')))
        self.gel_1004_pk = gel_1004_csv.pk
        receiving_rack = ReceivingRack.objects.create(gel_1004_csv=gel_1004_csv,
                                                      receiving_rack_id='SA12345678', laboratory_id='now',
                                                      glh_sample_consignment_number='abc-1234-12-12-12-1',
                                                      rack_acknowledged=False, disease_area='Rare Disease',
                                                      rack_type='Proband', priority='Routine')
        sample_one = Sample.objects.create(receiving_rack=receiving_rack,
                                           receiving_rack_well='A01', participant_id='p12345678901',
                                           group_id='r12345678901', priority='Routine',
                                           disease_area='Rare Disease', sample_type='Proband',
                                           clin_sample_type='dna_saliva', laboratory_sample_id='1234567890',
                                           uid='1234567890',
                                           laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                           tissue_type='Normal or Germline sample', sample_received=True)
        self.sample_two = Sample.objects.create(receiving_rack=receiving_rack,
                                           receiving_rack_well='B01', participant_id='p12345678902',
                                           group_id='r12345678902', priority='Routine',
                                           disease_area='Rare Disease', sample_type='Proband',
                                           clin_sample_type='dna_saliva', laboratory_sample_id='1234567891',
                                           uid='1234567891',
                                           laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                           tissue_type='Normal or Germline sample', sample_received=False)
        gel1008 = Gel1008Csv.objects.create(filename='ngis_bio_to_gel_sample_dispatch_20240212_093348.csv',
                                            report_generated_datetime=datetime.now(pytz.timezone('UTC')),
                                            date_of_dispatch=datetime(2020, 1, 1, tzinfo=pytz.UTC)
                                            )
        self.plate = Plate.objects.create(plate_id='LP1234816-DNA', gel_1008_csv=gel1008)
        holding_rack_one = HoldingRack.objects.create(holding_rack_id='tt12345673', discarded=False)

        for holding_rack_row in self.holding_rack_rows:
            for holding_rack_column in self.holding_rack_columns:
                HoldingRackWell.objects.create(holding_rack=holding_rack_one,
                                               well_id=holding_rack_row + holding_rack_column)

        self.holding_rack_well_one = HoldingRackWell.objects.get(
            holding_rack=holding_rack_one,
            well_id='A01')
        self.holding_rack_well_one.sample = sample_one
        self.holding_rack_well_one.save()

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
        holding_rack_two = HoldingRack.objects.create(holding_rack_id='tt12345678', plate=self.plate)
        for holding_rack_row in self.holding_rack_rows:
            for holding_rack_column in self.holding_rack_columns:
                HoldingRackWell.objects.create(holding_rack=holding_rack_two,
                                               well_id=holding_rack_row + holding_rack_column)
        holding_rack_well_two = HoldingRackWell.objects.get(
            holding_rack=holding_rack_two,
            well_id='A01')
        holding_rack_well_two.sample = self.sample_two
        holding_rack_well_two.save()
        response = self.client.get(reverse('discards:discards_index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discards/discard.html')
        self.assertContains(response, holding_rack_two.holding_rack_id)
        self.assertEqual(response.context['discard_racks'][0]['total'], 1)

    def test_discards_holding_racks(self):
        response = self._discard_holding_rack('tt12345673')
        holding_rack = HoldingRack.objects.get(holding_rack_id='tt12345673')
        sample = Sample.objects.get(laboratory_sample_id='1234567890')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Holding Racks discarded successfully')
        self.assertEqual(holding_rack.discarded, True)
        self.assertEqual(sample.discarded, True)
        # self.assertEqual(len(response.context['total']), 1)
        # self.assertEqual(response.context['holding_racks'][0].holding_rack_id, holding_rack.holding_rack_id)

    def test_discards_query(self):
        self._discard_holding_rack('tt12345673')
        response = self.client.get(reverse('discards:discards_index'), {'q': 'tt12345673'})
        self.assertContains(response, 'Holding Rack has been discarded')

    def test_discarded(self):
        self._discard_holding_rack('tt12345673')
        response = self.client.get(reverse('discards:all_discards_view'))
        self.assertEqual(response.context['data'][0].holding_rack_id, 'tt12345673')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discards/all_discards.html')


