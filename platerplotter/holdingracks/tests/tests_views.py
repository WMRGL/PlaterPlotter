from django.contrib.auth.models import User
from django.test import TestCase, Client

import os
import pytz
import glob
from datetime import datetime, date

from django.urls import reverse

from platerplotter.models import Gel1004Csv, ReceivingRack, Sample, Gel1005Csv, HoldingRack, HoldingRackWell


# Create your tests here.
class HoldingRackTestCase(TestCase):
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
        sample_one = Sample.objects.create(receiving_rack=receiving_rack,
                                           receiving_rack_well='A01', participant_id='p12345678901',
                                           group_id='r12345678901', priority='Routine',
                                           disease_area='Rare Disease', sample_type='Proband',
                                           clin_sample_type='dna_saliva', laboratory_sample_id='1234567890',
                                           uid='1234567890',
                                           laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                           tissue_type='Normal or Germline sample', sample_received=True)
        sample_two = Sample.objects.create(receiving_rack=receiving_rack,
                                           receiving_rack_well='B01', participant_id='p12345678902',
                                           group_id='r12345678902', priority='Routine',
                                           disease_area='Rare Disease', sample_type='Proband',
                                           clin_sample_type='dna_saliva', laboratory_sample_id='1234567891',
                                           uid='1234567891',
                                           laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                           tissue_type='Normal or Germline sample', sample_received=False)
        sample_three = Sample.objects.create(receiving_rack=receiving_rack,
                                             receiving_rack_well='C01', participant_id='p12345678908',
                                             group_id='r12345678908', priority='Routine',
                                             disease_area='Cancer', sample_type='Tumour',
                                             clin_sample_type='dna_saliva', laboratory_sample_id='1234567897',
                                             uid='1234567897',
                                             laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                             tissue_type='Normal or Germline sample', sample_received=True)
        receiving_rack_two = ReceivingRack.objects.create(gel_1004_csv=gel_1004_csv,
                                                          receiving_rack_id='SA12345679', laboratory_id='now',
                                                          glh_sample_consignment_number='abc-1234-12-12-12-1',
                                                          rack_acknowledged=False, disease_area='Rare Disease',
                                                          rack_type='Proband', priority='Routine')
        holding_rack = HoldingRack.objects.create(holding_rack_id='HH12345678')
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
        problem_holding_rack = HoldingRack.objects.create(holding_rack_id='PP12345678',
                                                          holding_rack_type='Problem')

    def test_load_holding_racks(self):
        response = self.client.get(reverse('holdingracks:holding_racks'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'holdingracks/holding-racks.html')
        self.assertContains(response, 'View current holding racks')
        self.assertContains(response, 'HH12345678')

    def test_load_holding_racks_with_holding_rack(self):
        response = self.client.get(reverse('holdingracks:holding_racks', kwargs={
            'holding_rack_id': 'HH12345678'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'holdingracks/holding-racks.html')
        self.assertContains(response, 'Holding rack')
        self.assertContains(response, 'HH12345678')

    def test_holding(self):
        response = self.client.post(reverse('holdingracks:holding_racks'), {
            'holding': [''], 'holding_rack_id': 'SA12345678'}, follow=True)
        self.assertContains(response, 'You have scanned an active receiving rack')
        # scanned a problem holding rack
        response = self.client.post(reverse('holdingracks:holding_racks'), {
            'holding': [''], 'holding_rack_id': 'PP12345678'}, follow=True)
        self.assertContains(response, 'You have scanned a holding rack being used for Problem samples')
        # scanned existing holding rack
        response = self.client.post(reverse('holdingracks:holding_racks'), {
            'holding': [''], 'holding_rack_id': 'HH12345678'}, follow=True)
        self.assertContains(response, 'Holding rack')
        self.assertContains(response, 'HH12345678')
        # scanned non existant holding rack
        self.assertFalse(HoldingRack.objects.filter(holding_rack_id='HH12345679'))
        response = self.client.post(reverse('holdingracks:holding_racks'), {
            'holding': [''], 'holding_rack_id': 'HH12345679'}, follow=True)
        self.assertContains(response, 'Holding rack not found with ID')

    def test_rack_scanner(self):
        response = self.client.post(reverse('holdingracks:holding_racks', kwargs={
            'holding_rack_id': 'HH12345678'}), {
                                        'rack-scanner': ['']}, follow=True)
        self.assertContains(response, 'not found')

    def test_ready_and_reopen(self):
        holding_rack = HoldingRack.objects.get(holding_rack_id='HH12345678')
        response = self.client.post(reverse('holdingracks:holding_racks', kwargs={
            'holding_rack_id': 'HH12345678'}), {
                                        'ready': holding_rack.pk}, follow=True)
        self.assertContains(response, 'Buffer will need to be added to the following wells')
        self.assertTrue(HoldingRackWell.objects.filter(holding_rack=holding_rack, buffer_added=True))
        response = self.client.post(reverse('holdingracks:holding_racks', kwargs={
            'holding_rack_id': 'HH12345678'}), {
                                        'reopen-rack': holding_rack.pk}, follow=True)
        self.assertFalse(HoldingRackWell.objects.filter(holding_rack=holding_rack, buffer_added=True))

    def test_log_issue(self):
        sample = Sample.objects.get(laboratory_sample_id='1234567890')
        response = self.client.post(reverse('holdingracks:holding_racks', kwargs={
            'holding_rack_id': 'HH12345678'}), {
                                        'log-issue': sample.pk, 'comment': 'issue identified'}, follow=True)
        sample = Sample.objects.get(laboratory_sample_id='1234567890')
        self.assertTrue(sample.issue_identified)
        self.assertEqual(sample.issue_outcome, 'Not resolved')
