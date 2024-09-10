from datetime import datetime

import pytz
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from platerplotter.models import Gel1004Csv, HoldingRack, ReceivingRack, Sample


# Create your tests here.

class ProblemSamplesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testing12345'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user.save()
        self.login = self.client.login(username=self.username, password=self.password)
        gel_1004_csv = Gel1004Csv.objects.create(filename='test1004.csv',
                                                 plating_organisation='wwm',
                                                 report_received_datetime=datetime.now(pytz.timezone('UTC')))
        self.gel_1004_pk = gel_1004_csv.pk
        holding_rack = HoldingRack.objects.create(holding_rack_id='HH12345678')
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
                                           tissue_type='Normal or Germline sample', sample_received=True,
                                           issue_identified=True, issue_outcome='Not resolved')
        sample_two = Sample.objects.create(receiving_rack=receiving_rack,
                                           receiving_rack_well='B01', participant_id='p12345678902',
                                           group_id='r12345678902', priority='Routine',
                                           disease_area='Rare Disease', sample_type='Proband',
                                           clin_sample_type='dna_saliva', laboratory_sample_id='1234567891',
                                           uid='1234567891',
                                           laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                           tissue_type='Normal or Germline sample', sample_received=False,
                                           issue_identified=True, issue_outcome='Not resolved')
        receiving_rack_two = ReceivingRack.objects.create(gel_1004_csv=gel_1004_csv,
                                                          receiving_rack_id='SA12345679', laboratory_id='now',
                                                          glh_sample_consignment_number='abc-1234-12-12-12-1',
                                                          rack_acknowledged=False, disease_area='Rare Disease',
                                                          rack_type='Proband', priority='Routine')

    def test_load_problem_samples(self):
        response = self.client.get(reverse('problemsamples:samples'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'problemsamples/problem-samples.html')
        self.assertContains(response, 'problem rack')

    def test_select_holding_rack(self):
        response = self.client.post(reverse('problemsamples:samples'), {
            'holding': [''], 'holding_rack_id': 'HH12345678'}, follow=True)
        self.assertContains(response, 'You have scanned a holding rack being used for')
        response = self.client.post(reverse('problemsamples:samples'), {
            'holding': [''], 'holding_rack_id': 'SA12345678'}, follow=True)
        self.assertContains(response, 'You have scanned an active receiving rack')
        response = self.client.post(reverse('problemsamples:samples'), {
            'holding': [''], 'holding_rack_id': 'SA12345679'}, follow=True)
        self.assertContains(response, 'Scan or type sample ID')
        self.assertTrue(HoldingRack.objects.get(holding_rack_id='SA12345679'))

    def test_add_sample(self):
        self.client.post(reverse('problemsamples:samples'), {
            'holding': [''], 'holding_rack_id': 'PP12345678'})
        response = self.client.post(reverse('problemsamples:problem_samples', kwargs={
            'holding_rack_id': 'PP12345678'}), {
                                        'sample': [''], 'lab_sample_id': '1234567890', 'well': ['']})
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').holding_rack_well.well_id, 'A01')
        response = self.client.post(reverse('problemsamples:problem_samples', kwargs={
            'holding_rack_id': 'PP12345678'}), {
                                        'sample': [''], 'lab_sample_id': '1234567891', 'well': ['']})
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567891').holding_rack_well.well_id, 'B01')

    def test_rack_scanner(self):
        self.client.post(reverse('problemsamples:samples'), {
            'holding': [''], 'holding_rack_id': 'PP12345678'})
        self.client.post(reverse('problemsamples:problem_samples', kwargs={
            'holding_rack_id': 'PP12345678'}), {
                             'sample': [''], 'lab_sample_id': '1234567890', 'well': ['']})
        self.client.post(reverse('problemsamples:problem_samples', kwargs={
            'holding_rack_id': 'PP12345678'}), {
                             'sample': [''], 'lab_sample_id': '1234567891', 'well': ['A02']})
        response = self.client.post(reverse('problemsamples:problem_samples', kwargs={
            'holding_rack_id': 'PP12345678', 'test_status': True}), {
                                        'rack-scanner': ['']})
        self.assertContains(response, 'not found')

    def test_log_delete_and_resolve_issue(self):
        pk = Sample.objects.get(laboratory_sample_id='1234567890').pk
        # log issue
        response = self.client.post(reverse('problemsamples:samples'), {
            'log-issue': pk, 'comment': 'issue logged'})
        self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').issue_identified)
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').comment, 'issue logged')
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').issue_outcome, 'Not resolved')
        # deleted issue
        response = self.client.post(reverse('problemsamples:samples'), {'delete-issue': pk})
        self.assertFalse(Sample.objects.get(laboratory_sample_id='1234567890').issue_identified)
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').comment, None)
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').issue_outcome, None)
        # log issue
        response = self.client.post(reverse('problemsamples:samples'), {
            'log-issue': pk, 'comment': 'issue logged'})
        self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').issue_identified)
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').comment, 'issue logged')
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').issue_outcome, 'Not resolved')
        # add sample to holding rack
        self.client.post(reverse('problemsamples:samples'), {
            'holding': [''], 'holding_rack_id': 'PP12345678'})
        response = self.client.post(reverse('problemsamples:problem_samples', kwargs={
            'holding_rack_id': 'PP12345678'}), {
                                        'sample': [''], 'lab_sample_id': '1234567890', 'well': ['']})
        # resolve issue
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').holding_rack_well.well_id, 'A01')
        response = self.client.post(reverse('problemsamples:problem_samples', kwargs={
            'holding_rack_id': 'PP12345678'}), {
                                        'resolve-issue': pk, 'comment': 'issue resolved',
                                        'issue_outcome': "Ready for plating"})
        self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').issue_identified)
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').comment, 'issue resolved')
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').issue_outcome, "Ready for plating")
        self.assertTrue(hasattr(Sample.objects.get(laboratory_sample_id='1234567890'), 'holding_rack_well'))
        # log issue
        response = self.client.post(reverse('problemsamples:samples'), {
            'log-issue': pk, 'comment': 'issue logged'})
        self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').issue_identified)
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').comment, 'issue logged')
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').issue_outcome, 'Not resolved')
        # add sample to holding rack
        self.client.post(reverse('problemsamples:samples'), {
            'holding': [''], 'holding_rack_id': 'PP12345678'})
        response = self.client.post(reverse('problemsamples:problem_samples', kwargs={
            'holding_rack_id': 'PP12345678'}), {
                                        'sample': [''], 'lab_sample_id': '1234567890', 'well': ['']})
        # resolve issue
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').holding_rack_well.well_id, 'A01')
        response = self.client.post(reverse('problemsamples:problem_samples', kwargs={
            'holding_rack_id': 'PP12345678'}), {
                                        'resolve-issue': pk, 'comment': 'issue resolved',
                                        'issue_outcome': "Sample destroyed"})
        self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').issue_identified)
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').comment, 'issue resolved')
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').issue_outcome, "Sample destroyed")
        self.assertFalse(hasattr(Sample.objects.get(laboratory_sample_id='1234567890'), 'holding_rack_well'))
