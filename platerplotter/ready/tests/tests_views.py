import glob
import os
from datetime import datetime
from pathlib import Path

import pytz
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from platerplotter.models import Gel1004Csv, Gel1005Csv, ReceivingRack, HoldingRack, HoldingRackWell, Sample, Plate


# Create your tests here.

class ReadyToPlateAndPlateHoldingRackTestCase(TestCase):
    def setUp(self):
        holding_rack_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        holding_rack_columns = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testing12345'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user.save()
        self.login = self.client.login(username=self.username, password=self.password)
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
        holding_rack = HoldingRack.objects.create(holding_rack_id='HH12345678',
                                                  ready_to_plate=True)
        for holding_rack_row in holding_rack_rows:
            for holding_rack_column in holding_rack_columns:
                HoldingRackWell.objects.create(holding_rack=holding_rack,
                                               well_id=holding_rack_row + holding_rack_column)
        sample_six = Sample.objects.create(receiving_rack=receiving_rack,
                                           receiving_rack_well='F01', participant_id='p12345678906',
                                           group_id='r12345678906', priority='Routine',
                                           disease_area='Rare Disease', sample_type='Proband',
                                           clin_sample_type='dna_saliva', laboratory_sample_id='1234567895',
                                           uid='1234567895',
                                           laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                           tissue_type='Normal or Germline sample', sample_received=True)
        sample_seven = Sample.objects.create(receiving_rack=receiving_rack,
                                             receiving_rack_well='G01', participant_id='p12345678907',
                                             group_id='r12345678907', priority='Routine',
                                             disease_area='Rare Disease', sample_type='Proband',
                                             clin_sample_type='dna_saliva', laboratory_sample_id='1234567896',
                                             uid='1234567896',
                                             laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                             tissue_type='Normal or Germline sample', sample_received=True,
                                             issue_identified=True, issue_outcome='Not resolved')
        holding_rack_well_three = HoldingRackWell.objects.get(
            holding_rack=holding_rack,
            well_id='A01')
        holding_rack_well_three.sample = sample_six
        holding_rack_well_three.save()
        holding_rack_well_four = HoldingRackWell.objects.get(
            holding_rack=holding_rack,
            well_id='E01')
        holding_rack_well_four.sample = sample_seven
        holding_rack_well_four.save()

    def test_ready_to_plate(self):
        response = self.client.get(reverse('ready:ready_to_plate'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ready/ready-to-plate.html')
        self.assertContains(response, 'Samples ready for plating')
        self.assertContains(response, 'HH12345678')

    def test_plate_holding_rack(self):
        holding_rack = HoldingRack.objects.get(holding_rack_id='HH12345678')
        response = self.client.get(reverse('holdingracks:plate_holding_rack', kwargs={
            'holding_rack_pk': holding_rack.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'holdingracks/plate-holding-rack.html')
        self.assertContains(response, 'Plate samples')
        self.assertContains(response, 'HH12345678')

    def test_rack_scanner(self):
        holding_rack = HoldingRack.objects.get(holding_rack_id='HH12345678')
        response = self.client.post(reverse('holdingracks:plate_holding_rack', kwargs={
            'holding_rack_pk': holding_rack.pk}), {
                                        'rack-scanner': ['']}, follow=True)
        self.assertContains(response, 'not found')

    def test_assign_plate(self):
        holding_rack = HoldingRack.objects.get(holding_rack_id='HH12345678')
        response = self.client.post(reverse('holdingracks:holding_racks', kwargs={
            'holding_rack_id': 'HH12345678'}), {
                                        'ready': holding_rack.pk}, follow=True)
        self.assertContains(response, 'Buffer will need to be added to the following wells')
        response = self.client.post(reverse('holdingracks:plate_holding_rack', kwargs={
            'holding_rack_pk': holding_rack.pk, 'test_status': True}), {
                                        "assign-plate": [''], "plate_id": "LP0000000-DNA"}, follow=True)
        self.assertTrue(Plate.objects.get(plate_id="LP0000000-DNA"))
        directory = str(Path.cwd().parent) + '/TestData/Outbound/PlatePlots/'
        self.assertEqual(len(os.listdir(directory)), 1)
        files = glob.glob(directory + '*')
        for f in files:
            os.remove(f)
        directory = str(Path.cwd().parent) + '/TestData/Outbound/PlatePlots/'
        self.assertEqual(len(os.listdir(directory)), 0)

    def test_add_comment(self):
        sample = Sample.objects.get(uid=1234567895)
        response = self.client.post(reverse('ready:sample_comment', kwargs={'pk': sample.pk}), {
            'comment': 'test comment'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('ready/audit.html')
        self.assertContains(response, 'Comment added successfully')
