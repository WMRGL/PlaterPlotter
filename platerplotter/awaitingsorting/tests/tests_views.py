from datetime import datetime

import pytz
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from platerplotter.models import Gel1005Csv, HoldingRack, Sample, ReceivingRack, HoldingRackWell, Gel1004Csv


# Create your tests here.

class AwaitingHoldingRackAssignmentTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testing12345'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user.save()
        self.login = self.client.login(username=self.username, password=self.password)
        gel_1005_csv = Gel1005Csv.objects.create(filename='test1005.csv',
                                                 report_generated_datetime=datetime.now(pytz.timezone('UTC')))
        gel_1004_csv = Gel1004Csv.objects.create(gel_1005_csv=gel_1005_csv,
                                                 filename='test1004.csv', plating_organisation='wwm',
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
                                           issue_identified=False)
        sample_two = Sample.objects.create(receiving_rack=receiving_rack,
                                           receiving_rack_well='B01', participant_id='p12345678902',
                                           group_id='r12345678902', priority='Routine',
                                           disease_area='Rare Disease', sample_type='Proband',
                                           clin_sample_type='dna_saliva', laboratory_sample_id='1234567891',
                                           uid='1234567891',
                                           laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                           tissue_type='Normal or Germline sample', sample_received=True,
                                           issue_identified=False)
        sample_three = Sample.objects.create(receiving_rack=receiving_rack,
                                             receiving_rack_well='C01', participant_id='p12345678903',
                                             group_id='r12345678903', priority='Routine',
                                             disease_area='Rare Disease', sample_type='Proband',
                                             clin_sample_type='dna_saliva', laboratory_sample_id='1234567892',
                                             uid='1234567892',
                                             laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                             tissue_type='Normal or Germline sample', sample_received=False,
                                             issue_identified=False)
        problem_holding_rack = HoldingRack.objects.create(holding_rack_id='PP12345678',
                                                          holding_rack_type='Problem')
        sample_four = Sample.objects.create(receiving_rack=receiving_rack,
                                            receiving_rack_well='D01', participant_id='p12345678904',
                                            group_id='r12345678904', priority='Routine',
                                            disease_area='Rare Disease', sample_type='Proband',
                                            clin_sample_type='dna_saliva', laboratory_sample_id='1234567893',
                                            uid='1234567893',
                                            laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                            tissue_type='Normal or Germline sample', sample_received=True,
                                            issue_identified=True, issue_outcome='Ready for plating')
        sample_five = Sample.objects.create(receiving_rack=receiving_rack,
                                            receiving_rack_well='E01', participant_id='p12345678905',
                                            group_id='r12345678905', priority='Routine',
                                            disease_area='Rare Disease', sample_type='Proband',
                                            clin_sample_type='dna_saliva', laboratory_sample_id='1234567894',
                                            uid='1234567894',
                                            laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                            tissue_type='Normal or Germline sample', sample_received=True,
                                            issue_identified=True, issue_outcome='Ready for plating')
        holding_rack_well_one = HoldingRackWell.objects.create(
            holding_rack=problem_holding_rack,
            well_id='A01', sample=sample_four)
        holding_rack_well_two = HoldingRackWell.objects.create(
            holding_rack=problem_holding_rack,
            well_id='B01', sample=sample_five)

    def test_load_awaiting_holding_rack_assignment(self):
        response = self.client.get(reverse('awaitingsorting:awaiting_holding_rack_assignment'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'awaitingsorting/awaiting-holding-rack-assignment.html')
        self.assertContains(response, 'Samples awaiting sorting')
        self.assertContains(response, 'GLH Racks')
        self.assertContains(response, '2')
        self.assertContains(response, 'Problem Racks')
        self.assertContains(response, 'Rare Disease')
        self.assertContains(response, 'Proband')
        self.assertContains(response, 'Routine')
        sample = Sample.objects.get(laboratory_sample_id='1234567891')
        sample.disease_area = "Cancer"
        sample.sample_type = "Tumour"
        sample.priority = "Urgent"
        sample.save()
        response = self.client.get(reverse('awaitingsorting:awaiting_holding_rack_assignment'))
        self.assertNotContains(response, 'Rare Disease')
        self.assertNotContains(response, 'Proband')
        self.assertNotContains(response, 'Routine')
        self.assertContains(response, 'Mixed')


class AssignSamplesToHoldingRackTestCase(TestCase):
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
        problem_holding_rack = HoldingRack.objects.create(holding_rack_id='PP12345678',
                                                          holding_rack_type='Problem')
        sample_four = Sample.objects.create(receiving_rack=receiving_rack,
                                            receiving_rack_well='D01', participant_id='p12345678904',
                                            group_id='r12345678904', priority='Routine',
                                            disease_area='Rare Disease', sample_type='Proband',
                                            clin_sample_type='dna_saliva', laboratory_sample_id='1234567893',
                                            uid='1234567893',
                                            laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                            tissue_type='Normal or Germline sample', sample_received=True,
                                            issue_identified=True, issue_outcome='Ready for plating')
        sample_five = Sample.objects.create(receiving_rack=receiving_rack,
                                            receiving_rack_well='E01', participant_id='p12345678905',
                                            group_id='r12345678905', priority='Routine',
                                            disease_area='Rare Disease', sample_type='Proband',
                                            clin_sample_type='dna_saliva', laboratory_sample_id='1234567894',
                                            uid='1234567894',
                                            laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                            tissue_type='Normal or Germline sample', sample_received=True,
                                            issue_identified=True, issue_outcome='Ready for plating')
        holding_rack_well_one = HoldingRackWell.objects.create(
            holding_rack=problem_holding_rack,
            well_id='A01', sample=sample_four)
        holding_rack_well_two = HoldingRackWell.objects.create(
            holding_rack=problem_holding_rack,
            well_id='B01', sample=sample_five)
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
        # create sample eight to test sample_delivery_mode 'Tumour First' in test_sample()
        sample_eight = Sample.objects.create(receiving_rack=receiving_rack,
                                             receiving_rack_well='H01', participant_id='p12345678709',
                                             group_id='r123456789709', priority='Routine',
                                             disease_area='Cancer', sample_type='Tumour',
                                             clin_sample_type='dna_saliva', laboratory_sample_id='1234567689',
                                             uid='1234567689',
                                             laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                             tissue_type='Solid tumour sample', sample_received=True,
                                             sample_delivery_mode='Tumour First')
        # create holding rack to test sample_delivery_mode in test_sample()
        tumour_holding_rack = HoldingRack.objects.create(holding_rack_id='HH87654321')
        for holding_rack_row in holding_rack_rows:
            for holding_rack_column in holding_rack_columns:
                HoldingRackWell.objects.create(holding_rack=tumour_holding_rack,
                                               well_id=holding_rack_row + holding_rack_column)

    def test_load_assign_samples_to_holding_rack_normal(self):
        gel_1004 = Gel1004Csv.objects.get(filename='test1004.csv')
        response = self.client.get(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'awaitingsorting/assign-samples-to-holding-rack.html')
        self.assertContains(response, 'Determine plate well locations for samples')
        self.assertContains(response, 'HH12345678')

    def test_load_assign_samples_to_holding_rack_problem(self):
        response = self.client.get(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'PP12345678'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'awaitingsorting/assign-samples-to-holding-rack.html')
        self.assertContains(response, 'Determine plate well locations for samples')
        self.assertContains(response, 'HH12345678')

    def test_load_assign_samples_to_holding_rack_normal_with_holding_rack(self):
        gel_1004 = Gel1004Csv.objects.get(filename='test1004.csv')
        response = self.client.get(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'awaitingsorting/assign-samples-to-holding-rack.html')
        self.assertContains(response, 'Samples awaiting well assignment')
        self.assertContains(response, 'HH12345678')

    def test_load_assign_samples_to_holding_rack_problem_with_holding_rack(self):
        response = self.client.get(reverse('awaitingsorting:assign_problem_samples_to_holding_rack', kwargs={
            'rack': 'PP12345678', 'holding_rack_id': 'HH12345678'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'awaitingsorting/assign-samples-to-holding-rack.html')
        self.assertContains(response, 'Samples awaiting well assignment')
        self.assertContains(response, 'HH12345678')

    def test_holding_post_gel_1004(self):
        gel_1004 = Gel1004Csv.objects.get(filename='test1004.csv')
        # scanned the receiveing rack
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk}), {
                                        'holding': [''], 'holding_rack_id': 'SA12345678'}, follow=True)
        self.assertContains(response, 'You have scanned the GMC Rack')
        # scanned a problem holding rack
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk}), {
                                        'holding': [''], 'holding_rack_id': 'PP12345678'}, follow=True)
        self.assertContains(response, 'You have scanned a holding rack for Problem samples')
        # scanned existing holding rack
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk}), {
                                        'holding': [''], 'holding_rack_id': 'HH12345678'}, follow=True)
        self.assertContains(response, 'Samples awaiting well assignment')
        self.assertContains(response, 'HH12345678')
        # scanned new holding rack
        self.assertFalse(HoldingRack.objects.filter(holding_rack_id='HH12345679'))
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk}), {
                                        'holding': [''], 'holding_rack_id': 'HH12345679'}, follow=True)
        self.assertContains(response, 'Samples awaiting well assignment')
        self.assertContains(response, 'HH12345679')
        self.assertTrue(HoldingRack.objects.filter(holding_rack_id='HH12345679'))

    def test_holding_post_without_gel_1004(self):
        # scanned the receiveing rack
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'PP12345678'}), {
                                        'holding': [''], 'holding_rack_id': 'SA12345678'}, follow=True)
        self.assertContains(response, 'You have scanned an active receiving rack')
        # scanned a problem holding rack
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'PP12345678'}), {
                                        'holding': [''], 'holding_rack_id': 'PP12345678'}, follow=True)
        self.assertContains(response, 'You have scanned a holding rack for Problem samples')
        # scanned existing holding rack
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'PP12345678'}), {
                                        'holding': [''], 'holding_rack_id': 'HH12345678'}, follow=True)
        self.assertContains(response, 'Samples awaiting well assignment')
        self.assertContains(response, 'HH12345678')
        # scanned new holding rack
        self.assertFalse(HoldingRack.objects.filter(holding_rack_id='HH12345679'))
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'PP12345678'}), {
                                        'holding': [''], 'holding_rack_id': 'HH12345679'}, follow=True)
        self.assertContains(response, 'Samples awaiting well assignment')
        self.assertContains(response, 'HH12345679')
        self.assertTrue(HoldingRack.objects.filter(holding_rack_id='HH12345679'))

    def test_rack_scanner(self):
        gel_1004 = Gel1004Csv.objects.get(filename='test1004.csv')
        # scanned the receiveing rack
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}), {
                                        'rack-scanner': ['']}, follow=True)
        self.assertContains(response, 'not found')

    def test_ready_and_reopen(self):
        gel_1004 = Gel1004Csv.objects.get(filename='test1004.csv')
        holding_rack = HoldingRack.objects.get(holding_rack_id='HH12345678')
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}), {
                                        'ready': holding_rack.pk}, follow=True)
        self.assertContains(response, 'Buffer will need to be added to the following wells')
        self.assertTrue(HoldingRackWell.objects.filter(holding_rack=holding_rack, buffer_added=True))
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}), {
                                        'reopen-rack': holding_rack.pk}, follow=True)
        self.assertFalse(HoldingRackWell.objects.filter(holding_rack=holding_rack, buffer_added=True))

    def test_sample(self):
        gel_1004 = Gel1004Csv.objects.get(filename='test1004.csv')
        sample = Sample.objects.get(laboratory_sample_id='1234567890')
        # not found in receiving rack
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}), {
                                        'sample': [''], 'lab_sample_id': '1234567896'}, follow=True)
        self.assertContains(response, 'not found in GLH Rack')
        # added to holding rack
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}), {
                                        'sample': [''], 'lab_sample_id': '1234567890', 'well': ['']}, follow=True)
        self.assertContains(response, 'assigned to well B01')
        # wrong sample type
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}), {
                                        'sample': [''], 'lab_sample_id': '1234567897', 'well': ['']}, follow=True)
        self.assertContains(response, 'Sample does not match holding rack type!')
        # assign with sample from problem plate
        response = self.client.post(reverse('awaitingsorting:assign_problem_samples_to_holding_rack', kwargs={
            'rack': 'PP12345678', 'holding_rack_id': 'HH12345678'}), {
                                        'sample': [''], 'lab_sample_id': '1234567893', 'well': ['']}, follow=True)
        self.assertContains(response, 'assigned to well C01')
        # wrong sample_delivery_mode
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH87654321'}), {
                                        'sample': [''], 'lab_sample_id': '1234567897', 'well': ['']}, follow=True)
        self.assertContains(response,
                            'No matching germline sample found for this sample. Unable to assign to holding rack.')
        # correct sample_delivery_mode 'Tumour First'
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH87654321'}), {
                                        'sample': [''], 'lab_sample_id': '1234567689', 'well': ['']}, follow=True)
        self.assertContains(response, 'assigned to well A01')

        # return sample without log issue
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}), {
                                        'return_rack': [''], 'return_sample': '1234567890',
                                        'return_holding_rack': 'PP12345678'}, follow=True)
        self.assertContains(response, 'Kindly log issue to sample')

        #return sample with issue
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}), {
                                        'log-issue': sample.pk, 'comment': 'issue identified'}, follow=True)

        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}), {
                                        'return_rack': [''], 'return_sample': '1234567890',
                                        'return_holding_rack': 'PP12345678'}, follow=True)
        self.assertContains(response, '1234567890 assigned to well')


    def test_log_issue_normal(self):
        gel_1004 = Gel1004Csv.objects.get(filename='test1004.csv')
        sample = Sample.objects.get(laboratory_sample_id='1234567890')
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk}), {
                                        'log-issue': sample.pk, 'comment': 'issue identified'}, follow=True)
        sample = Sample.objects.get(laboratory_sample_id='1234567890')
        self.assertTrue(sample.issue_identified)
        self.assertEqual(sample.issue_outcome, 'Not resolved')

    def test_log_issue_normal_on_holding_rack_page(self):
        gel_1004 = Gel1004Csv.objects.get(filename='test1004.csv')
        sample = Sample.objects.get(laboratory_sample_id='1234567890')
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}), {
                                        'log-issue': sample.pk, 'comment': 'issue identified'}, follow=True)
        sample = Sample.objects.get(laboratory_sample_id='1234567890')
        self.assertTrue(sample.issue_identified)
        self.assertEqual(sample.issue_outcome, 'Not resolved')

    def test_log_issue_problem(self):
        sample = Sample.objects.get(laboratory_sample_id='1234567890')
        response = self.client.post(reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
            'rack': 'PP12345678'}), {
                                        'log-issue': sample.pk, 'comment': 'issue identified'}, follow=True)
        sample = Sample.objects.get(laboratory_sample_id='1234567890')
        self.assertTrue(sample.issue_identified)
        self.assertEqual(sample.issue_outcome, 'Not resolved')

    def test_log_issue_problem_on_holding_rack_page(self):
        sample = Sample.objects.get(laboratory_sample_id='1234567890')
        response = self.client.post(reverse('awaitingsorting:assign_problem_samples_to_holding_rack', kwargs={
            'rack': 'PP12345678', 'holding_rack_id': 'HH12345678'}), {
                                        'log-issue': sample.pk, 'comment': 'issue identified'}, follow=True)
        sample = Sample.objects.get(laboratory_sample_id='1234567890')
        self.assertTrue(sample.issue_identified)
        self.assertEqual(sample.issue_outcome, 'Not resolved')
