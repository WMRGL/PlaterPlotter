from datetime import datetime

import pytz
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from charts.views import CancerRareDiseaseView
from platerplotter.models import Sample, ReceivingRack, Gel1004Csv, Gel1005Csv


class Chart(TestCase):

    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testing12345'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user.save()
        self.client.login(username=self.username, password=self.password)

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
        Sample.objects.create(receiving_rack=receiving_rack,
                                           receiving_rack_well='A01', participant_id='p12345678901',
                                           group_id='r12345678901', priority='Routine',
                                           disease_area='Rare Disease', sample_type='Proband',
                                           clin_sample_type='dna_saliva', laboratory_sample_id='1234567890',
                                           uid='1234567890',
                                           laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                           tissue_type='Normal or Germline sample', sample_received=True)
        Sample.objects.create(receiving_rack=receiving_rack,
                                           receiving_rack_well='C01', participant_id='p12345678908',
                                           group_id='r12345678908', priority='Routine',
                                           disease_area='Cancer', sample_type='Tumour',
                                           clin_sample_type='dna_saliva', laboratory_sample_id='1234567897',
                                           uid='1234567897',
                                           laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                           tissue_type='Normal or Germline sample', sample_received=True)
        self.cancer_rd = CancerRareDiseaseView()

    def test_chart(self):
        response = self.client.get(reverse('charts:cancer_rd'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'charts/cancer_rd.html')

    def test_get_total_disease_area(self):
        expected_result = {'cancer': 1, 'rare_disease': 1}
        self.assertEqual(self.cancer_rd.get_total_disease_counts(), expected_result)
