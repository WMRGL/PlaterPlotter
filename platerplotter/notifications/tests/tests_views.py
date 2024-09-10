import os
import pytz
import glob
from datetime import datetime, date

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from holdingracks.views import strip_zeros
from notifications.views import *
from platerplotter.models import Sample, ReceivingRack



# Create your tests here.

class ViewGEL1004InputValidationTestCase(TestCase):

    def test_pad_zeros(self):
        self.assertEqual(pad_zeros('A2'), 'A02')
        self.assertEqual(pad_zeros('A12'), 'A12')

    def test_strip_zeros(self):
        self.assertEqual(strip_zeros('A02'), 'A2')
        self.assertEqual(strip_zeros('A12'), 'A12')

    def test_check_plating_organisation(self):
        self.assertEqual(check_plating_organisation('WWM'), ('wwm', None))
        self.assertEqual(check_plating_organisation('abc'),
                         ('abc', 'Plating organisation entered as abc. Expected "wmm".'))

    def test_check_rack_id(self):
        self.assertEqual(check_rack_id('12345678'), ('12345678', None))
        self.assertEqual(check_rack_id('123456789012'), ('123456789012', None))
        self.assertEqual(check_rack_id('1234567'), (
            '1234567', 'Incorrect rack ID. Received 1234567 which does not match the required specification.'))
        self.assertEqual(check_rack_id('1234567890123'), (
            '1234567890123',
            'Incorrect rack ID. Received 1234567890123 which does not match the required specification.'))

    def test_check_laboratory_id(self):
        self.assertEqual(check_laboratory_id('NOW'), ('now', None))
        self.assertEqual(check_laboratory_id('NOO'), (
            'noo', 'Incorrect laboratory ID. Received NOO which is not on the list of accepted laboratory IDs.'))

    def test_check_participant_id(self):
        self.assertEqual(check_participant_id('P12345678901'), ('p12345678901', None))
        self.assertEqual(check_participant_id('P1234567890'), ('p1234567890',
                                                               'Incorrect participant ID. Received P1234567890 which does not match the required specification.'))

    def test_check_group_id(self):
        self.assertEqual(check_group_id('R12345678901'), ('r12345678901', None))
        self.assertEqual(check_group_id('R1234567890'), (
            'r1234567890', 'Incorrect group ID. Received R1234567890 which does not match the required specification.'))

    def test_check_priority(self):
        self.assertEqual(check_priority('routine'), ('Routine', None))
        self.assertEqual(check_priority('routinee'),
                         ('Routinee', 'Incorrect priority. Received routinee. Must be either routine or urgent.'))

    def test_check_disease_area(self):
        self.assertEqual(check_disease_area('cancer'), ('Cancer', None))
        self.assertEqual(check_disease_area('cancerr'), (
            'Cancerr', 'Incorrect disease area. Received cancerr. Must be either cancer or rare disease.'))

    # def test_check_clinical_sample_type(self):
    # 	self.assertEqual(check_clinical_sample_type('dna_saliva'), ('dna_saliva', None))
    # 	self.assertEqual(check_clinical_sample_type('dna'), ('dna', 'Clinical sample type not in list of accepted values. Received dna.'))

    def test_check_glh_sample_consignment_number(self):
        self.assertEqual(check_glh_sample_consignment_number('ABC-1234-12-12-12-1'), ('abc-1234-12-12-12-1', None))

    def test_check_laboratory_sample_id(self):
        self.assertEqual(check_laboratory_sample_id('1234567890'), ('1234567890', None))
        self.assertEqual(check_laboratory_sample_id('123456789'),
                         ('123456789', 'Incorrect laboratory sample ID. Received 123456789. Should be 10 digits'))

    def test_check_laboratory_sample_volume(self):
        self.assertEqual(check_laboratory_sample_volume('129304'), ('129304', None))
        self.assertEqual(check_laboratory_sample_volume('12930.4'),
                         ('12930.4', 'Incorrect laboratory sample volume. Received 12930.4. Should be all digits'))

    def test_check_rack_well(self):
        self.assertEqual(check_rack_well('h12'), ('H12', None))
        self.assertEqual(check_rack_well('i12'), ('I12', 'Invalid rack well for a 96 well rack. Received i12.'))
        self.assertEqual(check_rack_well('a19'), ('A19', 'Invalid rack well for a 96 well rack. Received a19.'))

    def test_check_is_proband(self):
        self.assertEqual(check_is_proband("TRUE"), (True, None))
        self.assertEqual(check_is_proband("True"), (True, None))
        self.assertEqual(check_is_proband("FALSE"), (False, None))
        self.assertEqual(check_is_proband("False"), (False, None))
        self.assertEqual(check_is_proband(True), (True, None))
        self.assertEqual(check_is_proband(False), (False, None))
        self.assertEqual(check_is_proband(1),
                         (1, 'Invalid value for Is Proband. Received 1 but expected a boolean value'))

    def test_check_is_repeat(self):
        self.assertEqual(check_is_repeat('REPEAT NEW'), ('Repeat New', None))
        self.assertEqual(check_is_repeat('REPEAT NE'),
                         ('Repeat Ne', 'Is repeat field not in list of accepted values. Received REPEAT NE.'))

    def test_check_tissue_type(self):
        self.assertEqual(check_tissue_type("Normal or Germline sample"), ("Normal or Germline sample", None))
        self.assertEqual(check_tissue_type("Normal or germline sample"), (
            "Normal or germline sample",
            'Tissue type not in list of accepted values. Received Normal or germline sample.'))

    def test_check_sample_delivery_mode(self):
        self.assertEqual(check_sample_delivery_mode("Standard"), ("Standard", None))
        self.assertEqual(check_sample_delivery_mode("Standar"), (
            "Standar", "Incorrect sample_delivery_mode. Received Standar which is not in the list of accepted values"))


class ImportAcksTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testing12345'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user.save()
        self.login = self.client.login(username=self.username, password=self.password)

    def test_import_acks(self):
        response = self.client.get(reverse(import_acks))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications/import-acks.html')
        self.assertContains(response, 'Unacknowledged Racks')
        response_post_import = self.client.post(reverse('notifications:index', kwargs={'test_status': True}),
                                                {'import-1004': ['']})
        self.assertEqual(Gel1004Csv.objects.count(), 1)
        self.assertEqual(ReceivingRack.objects.count(), 1)
        self.assertEqual(Sample.objects.count(), 7)
        # Test new Gel1004 file format NGIS spec v3.22
        os.rename(
            str(Path.cwd().parent) + '/TestData/Inbound/GEL1004/processed/ngis_gel_to_bio_sample_sent_eme_20190614_133158.csv',
            str(Path.cwd().parent) + '/TestData/Inbound/GEL1004/ngis_gel_to_bio_sample_sent_eme_20190614_133158.csv')
        response_post_import = self.client.post(reverse('notifications:index', kwargs={'test_status': True}),
                                                {'import-1004': ['']})
        self.assertEqual(Gel1004Csv.objects.count(), 2)
        self.assertEqual(ReceivingRack.objects.count(), 2)
        self.assertEqual(Sample.objects.count(), 14)
        os.rename(
            str(Path.cwd().parent) + '/TestData/Inbound/GEL1004/processed/ngis_gel_to_bio_sample_sent_eme_20190614_133157.csv',
            str(Path.cwd().parent) + '/TestData/Inbound/GEL1004/ngis_gel_to_bio_sample_sent_eme_20190614_133157.csv')


class SendGel1005TestCase(TestCase):
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
        receiving_rack = ReceivingRack.objects.create(gel_1004_csv=gel_1004_csv,
                                                      receiving_rack_id='SA12345678', laboratory_id='now',
                                                      glh_sample_consignment_number='abc-1234-12-12-12-1',
                                                      rack_acknowledged=True, disease_area='Rare Disease',
                                                      rack_type='Proband', priority='Routine')
        sample_one = Sample.objects.create(receiving_rack=receiving_rack,
                                           receiving_rack_well='A01', participant_id='p12345678901',
                                           group_id='r12345678901', priority='Routine',
                                           disease_area='Rare Disease', sample_type='Proband',
                                           clin_sample_type='dna_saliva', laboratory_sample_id='1234567890',
                                           uid='1234567890',
                                           laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                           tissue_type='Normal or Germline sample', sample_received=True,
                                           sample_received_datetime=datetime.now(pytz.timezone('UTC')))
        sample_two = Sample.objects.create(receiving_rack=receiving_rack,
                                           receiving_rack_well='B01', participant_id='p12345678902',
                                           group_id='r12345678902', priority='Routine',
                                           disease_area='Rare Disease', sample_type='Proband',
                                           clin_sample_type='dna_saliva', laboratory_sample_id='1234567891',
                                           uid='1234567891',
                                           laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                           tissue_type='Normal or Germline sample', sample_received=False)

    def test_generate_gel1005(self):
        response_post_gel1005 = self.client.post(reverse('notifications:index', kwargs={
            'test_status': True}), {'send-1005': self.gel_1004_pk})
        self.assertEqual(Gel1005Csv.objects.count(), 1)
        directory = str(Path.cwd().parent) + '/TestData/Outbound/GEL1005/'
        self.assertEqual(len(os.listdir(directory)), 1)
        files = glob.glob(directory + '*')
        for f in files:
            os.remove(f)


class AcknowledgeSamplesTestCase(TestCase):
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
                                           tissue_type='Normal or Germline sample', sample_received=False)
        sample_two = Sample.objects.create(receiving_rack=receiving_rack,
                                           receiving_rack_well='B01', participant_id='p12345678902',
                                           group_id='r12345678902', priority='Routine',
                                           disease_area='Rare Disease', sample_type='Proband',
                                           clin_sample_type='dna_saliva', laboratory_sample_id='1234567891',
                                           uid='1234567891',
                                           laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                                           tissue_type='Normal or Germline sample', sample_received=False)

    def test_load_acknowledge_samples(self):
        response = self.client.get(reverse('notifications:acknowledge_samples', kwargs={
            'gel1004': self.gel_1004_pk, 'rack': 'SA12345678'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications/acknowledge-samples.html')
        self.assertContains(response, 'Acknowledge Receipt of Samples')

    def test_acknowledge_samples(self):
        directory = str(Path.cwd().parent) + '/TestData/'
        os.rename(directory + 'TestFiles/rack_scan_test_2.csv', directory + 'Inbound/RackScanner/rack_scan_test_2.csv')
        response = self.client.post(reverse('notifications:acknowledge_samples', kwargs={
            'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {'rack-scanner': ['']})
        os.rename(directory + 'Inbound/RackScanner/processed/rack_scan_test_2.csv',
                  directory + 'TestFiles/rack_scan_test_2.csv')
        self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').sample_received)
        self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567891').sample_received)
        self.assertContains(response, 'All samples received')

    def test_acknowledge_samples_wrong_positions(self):
        directory = str(Path.cwd().parent) + '/TestData/'
        os.rename(directory + 'TestFiles/rack_scan_test_3.csv', directory + 'Inbound/RackScanner/rack_scan_test_3.csv')
        response = self.client.post(reverse('notifications:acknowledge_samples', kwargs={
            'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {'rack-scanner': ['']})
        os.rename(directory + 'Inbound/RackScanner/processed/rack_scan_test_3.csv',
                  directory + 'TestFiles/rack_scan_test_3.csv')
        self.assertFalse(Sample.objects.get(laboratory_sample_id='1234567890').sample_received)
        self.assertFalse(Sample.objects.get(laboratory_sample_id='1234567891').sample_received)
        self.assertContains(response, 'wrong')
        self.assertContains(response, 'missing')
        self.assertContains(response, 'extra')

    def test_no_rack_scan(self):
        response = self.client.post(reverse('notifications:acknowledge_samples', kwargs={
            'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {'rack-scanner': ['']})
        self.assertFalse(Sample.objects.get(laboratory_sample_id='1234567890').sample_received)
        self.assertFalse(Sample.objects.get(laboratory_sample_id='1234567891').sample_received)
        self.assertContains(response, 'not found')

    def test_acknowledge_rack(self):
        response = self.client.post(reverse('notifications:acknowledge_samples', kwargs={
            'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {'rack-acked': ['']})
        self.assertTrue(ReceivingRack.objects.get(receiving_rack_id='SA12345678').rack_acknowledged)

    def test_scan_sample(self):
        response = self.client.post(reverse('notifications:acknowledge_samples', kwargs={
            'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {'sample-scanned': [''],
                                                                                       'lab_sample_id': '1234567897'})
        self.assertContains(response, 'does not exist')
        self.assertFalse(Sample.objects.get(laboratory_sample_id='1234567890').sample_received)
        response = self.client.post(reverse('notifications:acknowledge_samples', kwargs={
            'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {'sample-scanned': [''],
                                                                                       'lab_sample_id': '1234567890'})
        self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').sample_received)

    def test_sample_received(self):
        pk = Sample.objects.get(laboratory_sample_id='1234567890').pk
        response = self.client.post(reverse('notifications:acknowledge_samples', kwargs={
            'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {'sample-received': pk})
        self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').sample_received)
        response = self.client.post(reverse('notifications:acknowledge_samples', kwargs={
            'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {'sample-received': pk})
        self.assertFalse(Sample.objects.get(laboratory_sample_id='1234567890').sample_received)

    def test_log_and_delete_issue(self):
        pk = Sample.objects.get(laboratory_sample_id='1234567890').pk
        response = self.client.post(reverse('notifications:acknowledge_samples', kwargs={
            'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {
                                        'log-issue': pk, 'comment': 'issue logged'})
        self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').issue_identified)
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').comment, 'issue logged')
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').issue_outcome, 'Not resolved')
        response = self.client.post(reverse('notifications:acknowledge_samples', kwargs={
            'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {
                                        'delete-issue': pk})
        self.assertFalse(Sample.objects.get(laboratory_sample_id='1234567890').issue_identified)
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').comment, None)
        self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').issue_outcome, None)
