from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from platerplotter.views import *
from platerplotter.models import *
import os
import pytz
import glob
from datetime import datetime


class ViewGEL1004InputValidationTestCase(TestCase):

	def test_pad_zeros(self):
		self.assertEqual(pad_zeros('A2'), 'A02')
		self.assertEqual(pad_zeros('A12'), 'A12')

	def test_strip_zeros(self):
		self.assertEqual(strip_zeros('A02'), 'A2')
		self.assertEqual(strip_zeros('A12'), 'A12')

	def test_check_plating_organisation(self):
		self.assertEqual(check_plating_organisation('WWM'), 'wwm')
		with self.assertRaises(ValueError):
			check_plating_organisation('abc')

	def test_check_rack_id(self):
		self.assertEqual(check_rack_id('12345678'), '12345678')
		self.assertEqual(check_rack_id('123456789012'), '123456789012')
		with self.assertRaises(ValueError):
			check_rack_id('1234567')
		with self.assertRaises(ValueError):
			check_rack_id('1234567890123')

	def test_check_laboratory_id(self):
		self.assertEqual(check_laboratory_id('NOW'), 'now')
		with self.assertRaises(ValueError):
			check_laboratory_id('NOO')

	def test_check_participant_id(self):
		self.assertEqual(check_participant_id('P12345678901'),'p12345678901')
		with self.assertRaises(ValueError):
			check_laboratory_id('P1234567890')

	def test_check_group_id(self):
		self.assertEqual(check_group_id('R12345678901'),'r12345678901')
		with self.assertRaises(ValueError):
			check_group_id('R1234567890')

	def test_check_priority(self):
		self.assertEqual(check_priority('routine'), 'ROUTINE')
		with self.assertRaises(ValueError):
			check_group_id('routinee')

	def test_check_disease_area(self):
		self.assertEqual(check_disease_area('cancer'), 'CANCER')
		with self.assertRaises(ValueError):
			check_disease_area('cancerr')

	def test_check_clinical_sample_type(self):
		self.assertEqual(check_clinical_sample_type('dna_saliva'), 'dna_saliva')
		with self.assertRaises(ValueError):
			check_clinical_sample_type('dna')

	def test_check_glh_sample_consignment_number(self):
		self.assertEqual(check_glh_sample_consignment_number('ABC-1234-12-12-12-1'), 'abc-1234-12-12-12-1')
		with self.assertRaises(ValueError):
			check_glh_sample_consignment_number('ABC-1234-12-12-12-3')

	def test_check_laboratory_sample_id(self):
		self.assertEqual(check_laboratory_sample_id('1234567890'), '1234567890')
		with self.assertRaises(ValueError):
			check_laboratory_sample_id('123456789')

	def test_check_laboratory_sample_volume(self):
		self.assertEqual(check_laboratory_sample_volume('129304'), '129304')
		with self.assertRaises(ValueError):
			check_laboratory_sample_volume('12930.4')

	def test_check_rack_well(self):
		self.assertEqual(check_rack_well('h12'), 'H12')
		with self.assertRaises(ValueError):
			check_rack_well('i12')

	def test_check_is_proband(self):
		self.assertTrue(check_is_proband("TRUE"))
		self.assertTrue(check_is_proband("True"))
		self.assertFalse(check_is_proband("FALSE"))
		self.assertFalse(check_is_proband("False"))
		self.assertTrue(check_is_proband(True))
		self.assertFalse(check_is_proband(False))
		with self.assertRaises(ValueError):
			check_is_proband(1)

	def test_check_is_repeat(self):
		self.assertEqual(check_is_repeat('REPEAT NEW'), 'Repeat New')
		with self.assertRaises(ValueError):
			check_is_repeat('REPEAT NE')

	def test_check_tissue_type(self):
		self.assertEqual(check_tissue_type("Normal or Germline sample"), "Normal or Germline sample")
		with self.assertRaises(ValueError):
			check_tissue_type("Normal or germline sample")

class ViewHelperFunctionsTestCase(TestCase):

	def test_rack_scan(self):
		directory = str(Path.cwd().parent) + '/TestData/'
		os.rename(directory + 'TestFiles/rack_scan_test_1.csv', directory + 'Inbound/RackScanner/rack_scan_test_1.csv')
		rack_scan(test_status=True)
		self.assertEqual(RackScanner.objects.count(), 1)
		self.assertEqual(RackScannerSample.objects.count(), 4)
		os.rename(directory + 'Inbound/RackScanner/processed/rack_scan_test_1.csv', directory + 'TestFiles/rack_scan_test_1.csv')
		os.rename(directory + 'TestFiles/rack_scan_test_1.csv', directory + 'Inbound/RackScanner/rack_scan_test_1.csv')
		rack_scan(test_status=True)
		self.assertEqual(RackScanner.objects.count(), 1)
		self.assertEqual(RackScannerSample.objects.count(), 4)
		os.rename(directory + 'Inbound/RackScanner/processed/rack_scan_test_1.csv', directory + 'TestFiles/rack_scan_test_1.csv')

	# def test_confirm_sample_positions(self):
	# 	c = Client()
	# 	request = c.get(reverse(import_acks))
	# 	print(request)
	# 	os.rename(str(Path.cwd().parent) + '/TestData/Inbound/RackScanner/processed/rack_scan_test_file.csv',
	# 		str(Path.cwd().parent) + '/TestData/Inbound/RackScanner/rack_scan_test_file.csv')

class LoginTestCase(TestCase):
	def setUp(self):
		self.client = Client()
		self.username = 'testuser'
		self.password = 'testing12345'
		self.user = User.objects.create_user(username=self.username, password=self.password)
		self.user.save()
		self.login = self.client.login(username=self.username, password=self.password)

	def test_login(self):
		self.assertTrue(self.login)

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
		self.assertTemplateUsed(response, 'platerplotter/import-acks.html')
		self.assertContains(response, 'Unacknowledged Racks')
		response_post_import = self.client.post(reverse(import_acks, kwargs={'test_status': True}), {'import-1004': ['']})
		self.assertEqual(Gel1004Csv.objects.count(), 1)
		self.assertEqual(ReceivingRack.objects.count(), 1)
		self.assertEqual(Sample.objects.count(), 7)
		os.rename(str(Path.cwd().parent) + '/TestData/Inbound/GEL1004/processed/ngis_gel_to_bio_sample_sent_eme_20190614_133157.csv',
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
			plating_organisation='wwm', report_received_datetime=datetime.now(pytz.timezone('UTC')))
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
			laboratory_sample_volume=10, is_proband=True, is_repeat='New',
			tissue_type='Normal or Germline sample', sample_received=True,
			sample_received_datetime=datetime.now(pytz.timezone('UTC')))
		sample_two = Sample.objects.create(receiving_rack=receiving_rack,
			receiving_rack_well='B01', participant_id='p12345678902',
			group_id='r12345678902', priority='Routine',
			disease_area='Rare Disease', sample_type='Proband',
			clin_sample_type='dna_saliva', laboratory_sample_id='1234567891',
			laboratory_sample_volume=10, is_proband=True, is_repeat='New',
			tissue_type='Normal or Germline sample', sample_received=False)

	def test_generate_gel1005(self):
		response_post_gel1005 = self.client.post(reverse(import_acks, kwargs={
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
			plating_organisation='wwm', report_received_datetime=datetime.now(pytz.timezone('UTC')))
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
			laboratory_sample_volume=10, is_proband=True, is_repeat='New',
			tissue_type='Normal or Germline sample', sample_received=False)
		sample_two = Sample.objects.create(receiving_rack=receiving_rack,
			receiving_rack_well='B01', participant_id='p12345678902',
			group_id='r12345678902', priority='Routine',
			disease_area='Rare Disease', sample_type='Proband',
			clin_sample_type='dna_saliva', laboratory_sample_id='1234567891',
			laboratory_sample_volume=10, is_proband=True, is_repeat='New',
			tissue_type='Normal or Germline sample', sample_received=False)

	def test_load_acknowledge_samples(self):
		response = self.client.get(reverse(acknowledge_samples, kwargs={
			'gel1004': self.gel_1004_pk, 'rack': 'SA12345678'}))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'platerplotter/acknowledge-samples.html')
		self.assertContains(response, 'Acknowledge Receipt of Samples')
		
	def test_acknowledge_samples(self):
		directory = str(Path.cwd().parent) + '/TestData/'
		os.rename(directory + 'TestFiles/rack_scan_test_2.csv', directory + 'Inbound/RackScanner/rack_scan_test_2.csv')
		response = self.client.post(reverse(acknowledge_samples, kwargs={
			'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {'rack-scanner': ['']})
		os.rename(directory + 'Inbound/RackScanner/processed/rack_scan_test_2.csv', directory + 'TestFiles/rack_scan_test_2.csv')
		self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').sample_received)
		self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567891').sample_received)
		self.assertContains(response, 'All samples received')

	def test_acknowledge_samples_wrong_positions(self):
		directory = str(Path.cwd().parent) + '/TestData/'
		os.rename(directory + 'TestFiles/rack_scan_test_3.csv', directory + 'Inbound/RackScanner/rack_scan_test_3.csv')
		response = self.client.post(reverse(acknowledge_samples, kwargs={
			'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {'rack-scanner': ['']})
		os.rename(directory + 'Inbound/RackScanner/processed/rack_scan_test_3.csv', directory + 'TestFiles/rack_scan_test_3.csv')
		self.assertFalse(Sample.objects.get(laboratory_sample_id='1234567890').sample_received)
		self.assertFalse(Sample.objects.get(laboratory_sample_id='1234567891').sample_received)
		self.assertContains(response, 'wrong')
		self.assertContains(response, 'missing')
		self.assertContains(response, 'extra')

	def test_no_rack_scan(self):
		response = self.client.post(reverse(acknowledge_samples, kwargs={
			'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {'rack-scanner': ['']})
		self.assertFalse(Sample.objects.get(laboratory_sample_id='1234567890').sample_received)
		self.assertFalse(Sample.objects.get(laboratory_sample_id='1234567891').sample_received)
		self.assertContains(response, 'not found')

	def test_acknowledge_rack(self):
		response = self.client.post(reverse(acknowledge_samples, kwargs={
			'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {'rack-acked': ['']})
		self.assertTrue(ReceivingRack.objects.get(receiving_rack_id='SA12345678').rack_acknowledged)

	def test_scan_sample(self):
		response = self.client.post(reverse(acknowledge_samples, kwargs={
			'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {'sample-scanned': [''], 
			'lab_sample_id':'1234567897'})
		self.assertContains(response, 'does not exist')
		self.assertFalse(Sample.objects.get(laboratory_sample_id='1234567890').sample_received)
		response = self.client.post(reverse(acknowledge_samples, kwargs={	
			'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {'sample-scanned': [''], 
			'lab_sample_id':'1234567890'})
		self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').sample_received)

	def test_sample_received(self):
		pk = Sample.objects.get(laboratory_sample_id='1234567890').pk
		response = self.client.post(reverse(acknowledge_samples, kwargs={
			'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {'sample-received': pk})
		self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').sample_received)
		response = self.client.post(reverse(acknowledge_samples, kwargs={
			'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {'sample-received': pk})
		self.assertFalse(Sample.objects.get(laboratory_sample_id='1234567890').sample_received)

	def test_log_and_delete_issue(self):
		pk = Sample.objects.get(laboratory_sample_id='1234567890').pk
		response = self.client.post(reverse(acknowledge_samples, kwargs={
			'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {
			'log-issue': pk, 'comment': 'issue logged'})
		self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').issue_identified)
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').comment, 'issue logged')
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').issue_outcome, 'Not resolved')
		response = self.client.post(reverse(acknowledge_samples, kwargs={
			'gel1004': self.gel_1004_pk, 'rack': 'SA12345678', 'test_status': True}), {
			'delete-issue': pk})
		self.assertFalse(Sample.objects.get(laboratory_sample_id='1234567890').issue_identified)
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').comment, None)
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').issue_outcome, None)

class ProblemSamplesTestCase(TestCase):
	def setUp(self):
		self.client = Client()
		self.username = 'testuser'
		self.password = 'testing12345'
		self.user = User.objects.create_user(username=self.username, password=self.password)
		self.user.save()
		self.login = self.client.login(username=self.username, password=self.password)
		gel_1004_csv = Gel1004Csv.objects.create(filename='test1004.csv',
			plating_organisation='wwm', report_received_datetime=datetime.now(pytz.timezone('UTC')))
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
			laboratory_sample_volume=10, is_proband=True, is_repeat='New',
			tissue_type='Normal or Germline sample', sample_received=True,
			issue_identified=True, issue_outcome='Not resolved')
		sample_two = Sample.objects.create(receiving_rack=receiving_rack,
			receiving_rack_well='B01', participant_id='p12345678902',
			group_id='r12345678902', priority='Routine',
			disease_area='Rare Disease', sample_type='Proband',
			clin_sample_type='dna_saliva', laboratory_sample_id='1234567891',
			laboratory_sample_volume=10, is_proband=True, is_repeat='New',
			tissue_type='Normal or Germline sample', sample_received=False,
			issue_identified=True, issue_outcome='Not resolved')
		receiving_rack_two = ReceivingRack.objects.create(gel_1004_csv=gel_1004_csv,
			receiving_rack_id='SA12345679', laboratory_id='now', 
			glh_sample_consignment_number='abc-1234-12-12-12-1',
			rack_acknowledged=False, disease_area='Rare Disease',
			rack_type='Proband', priority='Routine')

	def test_load_problem_samples(self):
		response = self.client.get(reverse(problem_samples))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'platerplotter/problem-samples.html')
		self.assertContains(response, 'problem rack')

	def test_select_holding_rack(self):
		response = self.client.post(reverse(problem_samples), {
			'holding': [''], 'holding_rack_id': 'HH12345678'}, follow=True)
		self.assertContains(response, 'You have scanned a holding rack being used for')
		response = self.client.post(reverse(problem_samples), {
			'holding': [''], 'holding_rack_id': 'SA12345678'}, follow=True)
		self.assertContains(response, 'You have scanned an active receiving rack')
		response = self.client.post(reverse(problem_samples), {
			'holding': [''], 'holding_rack_id': 'SA12345679'}, follow=True)
		self.assertContains(response, 'Scan or type sample ID')
		self.assertTrue(HoldingRack.objects.get(holding_rack_id='SA12345679'))

	def test_add_sample(self):
		self.client.post(reverse(problem_samples), {
			'holding': [''], 'holding_rack_id': 'PP12345678'})
		response = self.client.post(reverse(problem_samples, kwargs={
			'holding_rack_id': 'PP12345678'}), {
			'sample': [''], 'lab_sample_id': '1234567890', 'well':['']})
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').holding_rack_well.well_id, 'A01')
		response = self.client.post(reverse(problem_samples, kwargs={
			'holding_rack_id': 'PP12345678'}), {
			'sample': [''], 'lab_sample_id': '1234567891', 'well':['']})
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567891').holding_rack_well.well_id, 'B01')

	def test_rack_scanner(self):
		self.client.post(reverse(problem_samples), {
			'holding': [''], 'holding_rack_id': 'PP12345678'})
		self.client.post(reverse(problem_samples, kwargs={
			'holding_rack_id': 'PP12345678'}), {
			'sample': [''], 'lab_sample_id': '1234567890', 'well':['']})
		self.client.post(reverse(problem_samples, kwargs={
			'holding_rack_id': 'PP12345678'}), {
			'sample': [''], 'lab_sample_id': '1234567891', 'well':['A02']})
		response = self.client.post(reverse(problem_samples, kwargs={
			'holding_rack_id': 'PP12345678', 'test_status': True}), {
			'rack-scanner': ['']})
		self.assertContains(response, 'not found')

