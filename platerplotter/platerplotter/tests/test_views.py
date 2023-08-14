from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from platerplotter.views import *
from platerplotter.models import *
import os
import pytz
import glob
from datetime import datetime, date


class ViewGEL1004InputValidationTestCase(TestCase):

	def test_pad_zeros(self):
		self.assertEqual(pad_zeros('A2'), 'A02')
		self.assertEqual(pad_zeros('A12'), 'A12')

	def test_strip_zeros(self):
		self.assertEqual(strip_zeros('A02'), 'A2')
		self.assertEqual(strip_zeros('A12'), 'A12')

	def test_check_plating_organisation(self):
		self.assertEqual(check_plating_organisation('WWM'), ('wwm', None))
		self.assertEqual(check_plating_organisation('abc'), ('abc', 'Plating orgnaisation entered as abc. Expected "wmm".'))

	def test_check_rack_id(self):
		self.assertEqual(check_rack_id('12345678'), ('12345678', None))
		self.assertEqual(check_rack_id('123456789012'), ('123456789012', None))
		self.assertEqual(check_rack_id('1234567'), ('1234567', 'Incorrect rack ID. Received 1234567 which does not match the required specification.'))
		self.assertEqual(check_rack_id('1234567890123'), ('1234567890123', 'Incorrect rack ID. Received 1234567890123 which does not match the required specification.'))

	def test_check_laboratory_id(self):
		self.assertEqual(check_laboratory_id('NOW'), ('now', None))
		self.assertEqual(check_laboratory_id('NOO'), ('noo', 'Incorrect laboratory ID. Received NOO which is not on the list of accepted laboratory IDs.'))

	def test_check_participant_id(self):
		self.assertEqual(check_participant_id('P12345678901'),('p12345678901', None))
		self.assertEqual(check_participant_id('P1234567890'),('p1234567890', 'Incorrect participant ID. Received P1234567890 which does not match the required specification.'))

	def test_check_group_id(self):
		self.assertEqual(check_group_id('R12345678901'),('r12345678901', None))
		self.assertEqual(check_group_id('R1234567890'),('r1234567890', 'Incorrect group ID. Received R1234567890 which does not match the required specification.'))

	def test_check_priority(self):
		self.assertEqual(check_priority('routine'), ('Routine', None))
		self.assertEqual(check_priority('routinee'), ('Routinee', 'Incorrect priority. Received routinee. Must be either routine or urgent.'))

	def test_check_disease_area(self):
		self.assertEqual(check_disease_area('cancer'), ('Cancer', None))
		self.assertEqual(check_disease_area('cancerr'), ('Cancerr', 'Incorrect disease area. Received cancerr. Must be either cancer or rare disease.'))

	# def test_check_clinical_sample_type(self):
	# 	self.assertEqual(check_clinical_sample_type('dna_saliva'), ('dna_saliva', None))
	# 	self.assertEqual(check_clinical_sample_type('dna'), ('dna', 'Clinical sample type not in list of accepted values. Received dna.'))

	def test_check_glh_sample_consignment_number(self):
		self.assertEqual(check_glh_sample_consignment_number('ABC-1234-12-12-12-1'), ('abc-1234-12-12-12-1', None))

	def test_check_laboratory_sample_id(self):
		self.assertEqual(check_laboratory_sample_id('1234567890'), ('1234567890', None))
		self.assertEqual(check_laboratory_sample_id('123456789'), ('123456789', 'Incorrect laboratory sample ID. Received 123456789. Should be 10 digits'))

	def test_check_laboratory_sample_volume(self):
		self.assertEqual(check_laboratory_sample_volume('129304'), ('129304', None))
		self.assertEqual(check_laboratory_sample_volume('12930.4'), ('12930.4', 'Incorrect laboratory sample volume. Received 12930.4. Should be all digits'))

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
		self.assertEqual(check_is_proband(1), (1, 'Invalid value for Is Proband. Received 1 but expected a boolean value'))

	def test_check_is_repeat(self):
		self.assertEqual(check_is_repeat('REPEAT NEW'), ('Repeat New', None))
		self.assertEqual(check_is_repeat('REPEAT NE'), ('Repeat Ne', 'Is repeat field not in list of accepted values. Received REPEAT NE.'))

	def test_check_tissue_type(self):
		self.assertEqual(check_tissue_type("Normal or Germline sample"), ("Normal or Germline sample", None))
		self.assertEqual(check_tissue_type("Normal or germline sample"), ("Normal or germline sample", 'Tissue type not in list of accepted values. Received Normal or germline sample.'))

	def test_check_sample_delivery_mode(self):
		self.assertEqual(check_sample_delivery_mode("Standard"), ("Standard", None))
		self.assertEqual(check_sample_delivery_mode("Standar"), ("Standar", "Incorrect sample_delivery_mode. Received Standar which is not in the list of accepted values"))

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

class LoginAndRegisterTestCase(TestCase):
	def setUp(self):
		self.client = Client()
		self.username = 'testuser'
		self.password = 'testing12345'
		self.user = User.objects.create_user(username=self.username, password=self.password)
		self.user.save()
		self.login = self.client.login(username=self.username, password=self.password)

	def test_login(self):
		self.assertTrue(self.login)

	def test_register(self):
		response = self.client.get(reverse(register))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'registration/register.html')
		self.assertContains(response, 'Register')
		post_response = self.client.post(reverse(register), {'username': 'testuser1', 'password': 'testing123',
															 'email': 'test@gmail.com'})
		self.assertContains(post_response, 'created')

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
		# Test new Gel1004 file format NGIS spec v3.22
		os.rename(str(Path.cwd().parent) + '/TestData/Inbound/GEL1004/processed/ngis_gel_to_bio_sample_sent_eme_20190614_133158.csv',
			str(Path.cwd().parent) + '/TestData/Inbound/GEL1004/ngis_gel_to_bio_sample_sent_eme_20190614_133158.csv')
		response_post_import = self.client.post(reverse(import_acks, kwargs={'test_status': True}),	{'import-1004': ['']})
		self.assertEqual(Gel1004Csv.objects.count(), 2)
		self.assertEqual(ReceivingRack.objects.count(), 2)
		self.assertEqual(Sample.objects.count(), 14)
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

	def test_log_delete_and_resolve_issue(self):
		pk = Sample.objects.get(laboratory_sample_id='1234567890').pk
		# log issue
		response = self.client.post(reverse(problem_samples), {
			'log-issue': pk, 'comment': 'issue logged'})
		self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').issue_identified)
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').comment, 'issue logged')
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').issue_outcome, 'Not resolved')
		# deleted issue
		response = self.client.post(reverse(problem_samples), {'delete-issue': pk})
		self.assertFalse(Sample.objects.get(laboratory_sample_id='1234567890').issue_identified)
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').comment, None)
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').issue_outcome, None)
		# log issue
		response = self.client.post(reverse(problem_samples), {
			'log-issue': pk, 'comment': 'issue logged'})
		self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').issue_identified)
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').comment, 'issue logged')
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').issue_outcome, 'Not resolved')
		# add sample to holding rack
		self.client.post(reverse(problem_samples), {
			'holding': [''], 'holding_rack_id': 'PP12345678'})
		response = self.client.post(reverse(problem_samples, kwargs={
			'holding_rack_id': 'PP12345678'}), {
			'sample': [''], 'lab_sample_id': '1234567890', 'well':['']})
		# resolve issue
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').holding_rack_well.well_id, 'A01')
		response = self.client.post(reverse(problem_samples, kwargs={
			'holding_rack_id': 'PP12345678'}), {
			'resolve-issue': pk, 'comment': 'issue resolved', 'issue_outcome': "Ready for plating"})
		self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').issue_identified)
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').comment, 'issue resolved')
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').issue_outcome, "Ready for plating")
		self.assertTrue(hasattr(Sample.objects.get(laboratory_sample_id='1234567890'), 'holding_rack_well'))
		# log issue
		response = self.client.post(reverse(problem_samples), {
			'log-issue': pk, 'comment': 'issue logged'})
		self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').issue_identified)
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').comment, 'issue logged')
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').issue_outcome, 'Not resolved')
		# add sample to holding rack
		self.client.post(reverse(problem_samples), {
			'holding': [''], 'holding_rack_id': 'PP12345678'})
		response = self.client.post(reverse(problem_samples, kwargs={
			'holding_rack_id': 'PP12345678'}), {
			'sample': [''], 'lab_sample_id': '1234567890', 'well':['']})
		# resolve issue
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').holding_rack_well.well_id, 'A01')
		response = self.client.post(reverse(problem_samples, kwargs={
			'holding_rack_id': 'PP12345678'}), {
			'resolve-issue': pk, 'comment': 'issue resolved', 'issue_outcome': "Sample destroyed"})
		self.assertTrue(Sample.objects.get(laboratory_sample_id='1234567890').issue_identified)
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').comment, 'issue resolved')
		self.assertEqual(Sample.objects.get(laboratory_sample_id='1234567890').issue_outcome, "Sample destroyed")
		self.assertFalse(hasattr(Sample.objects.get(laboratory_sample_id='1234567890'), 'holding_rack_well'))

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
			holding_rack = problem_holding_rack,
			well_id = 'A01', sample = sample_four)
		holding_rack_well_two = HoldingRackWell.objects.create(
			holding_rack = problem_holding_rack,
			well_id = 'B01', sample = sample_five)

	def test_load_awaiting_holding_rack_assignment(self):
		response = self.client.get(reverse(awaiting_holding_rack_assignment))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'platerplotter/awaiting-holding-rack-assignment.html')
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
		response = self.client.get(reverse(awaiting_holding_rack_assignment))
		self.assertNotContains(response, 'Rare Disease')
		self.assertNotContains(response, 'Proband')
		self.assertNotContains(response, 'Routine')
		self.assertContains(response, 'Mixed')

class AssignSamplesToHoldingRackTestCase(TestCase):
	def setUp(self):
		holding_rack_rows = ['A','B','C','D','E','F','G','H']
		holding_rack_columns = ['01','02','03','04','05','06','07','08','09','10','11','12']
		self.client = Client()
		self.username = 'testuser'
		self.password = 'testing12345'
		self.user = User.objects.create_user(username=self.username, password=self.password)
		self.user.save()
		self.login = self.client.login(username=self.username, password=self.password)
		gel_1005_csv = Gel1005Csv.objects.create(filename='test1005.csv',
			report_generated_datetime=datetime.now(pytz.timezone('UTC')))
		gel_1004_csv = Gel1004Csv.objects.create(filename='test1004.csv', gel_1005_csv=gel_1005_csv,
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
			holding_rack = problem_holding_rack,
			well_id = 'A01', sample = sample_four)
		holding_rack_well_two = HoldingRackWell.objects.create(
			holding_rack = problem_holding_rack,
			well_id = 'B01', sample = sample_five)
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
			holding_rack = holding_rack,
			well_id = 'A01')
		holding_rack_well_three.sample = sample_six
		holding_rack_well_three.save()
		holding_rack_well_four = HoldingRackWell.objects.get(
			holding_rack = holding_rack,
			well_id = 'E01')
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
		response = self.client.get(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'SA12345678', 'gel1004': gel_1004.pk}))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'platerplotter/assign-samples-to-holding-rack.html')
		self.assertContains(response, 'Determine plate well locations for samples')
		self.assertContains(response, 'HH12345678')

	def test_load_assign_samples_to_holding_rack_problem(self):
		response = self.client.get(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'PP12345678'}))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'platerplotter/assign-samples-to-holding-rack.html')
		self.assertContains(response, 'Determine plate well locations for samples')
		self.assertContains(response, 'HH12345678')

	def test_load_assign_samples_to_holding_rack_normal_with_holding_rack(self):
		gel_1004 = Gel1004Csv.objects.get(filename='test1004.csv')
		response = self.client.get(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'platerplotter/assign-samples-to-holding-rack.html')
		self.assertContains(response, 'Samples awaiting well assignment')
		self.assertContains(response, 'HH12345678')

	def test_load_assign_samples_to_holding_rack_problem_with_holding_rack(self):
		response = self.client.get(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'PP12345678', 'holding_rack_id': 'HH12345678'}))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'platerplotter/assign-samples-to-holding-rack.html')
		self.assertContains(response, 'Samples awaiting well assignment')
		self.assertContains(response, 'HH12345678')

	def test_holding_post_gel_1004(self):
		gel_1004 = Gel1004Csv.objects.get(filename='test1004.csv')
		# scanned the receiveing rack
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'SA12345678', 'gel1004': gel_1004.pk}), {
			'holding': [''], 'holding_rack_id': 'SA12345678'}, follow=True)
		self.assertContains(response, 'You have scanned the GMC Rack')
		# scanned a problem holding rack
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'SA12345678', 'gel1004': gel_1004.pk}), {
			'holding': [''], 'holding_rack_id': 'PP12345678'}, follow=True)
		self.assertContains(response, 'You have scanned a holding rack for Problem samples')
		# scanned existing holding rack
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'SA12345678', 'gel1004': gel_1004.pk}), {
			'holding': [''], 'holding_rack_id': 'HH12345678'}, follow=True)
		self.assertContains(response, 'Samples awaiting well assignment')
		self.assertContains(response, 'HH12345678')
		# scanned new holding rack
		self.assertFalse(HoldingRack.objects.filter(holding_rack_id='HH12345679'))
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'SA12345678', 'gel1004': gel_1004.pk}), {
			'holding': [''], 'holding_rack_id': 'HH12345679'}, follow=True)
		self.assertContains(response, 'Samples awaiting well assignment')
		self.assertContains(response, 'HH12345679')
		self.assertTrue(HoldingRack.objects.filter(holding_rack_id='HH12345679'))

	def test_holding_post_without_gel_1004(self):
		# scanned the receiveing rack
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'PP12345678'}), {
			'holding': [''], 'holding_rack_id': 'SA12345678'}, follow=True)
		self.assertContains(response, 'You have scanned an active receiving rack')
		# scanned a problem holding rack
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'PP12345678'}), {
			'holding': [''], 'holding_rack_id': 'PP12345678'}, follow=True)
		self.assertContains(response, 'You have scanned a holding rack for Problem samples')
		# scanned existing holding rack
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'PP12345678'}), {
			'holding': [''], 'holding_rack_id': 'HH12345678'}, follow=True)
		self.assertContains(response, 'Samples awaiting well assignment')
		self.assertContains(response, 'HH12345678')
		# scanned new holding rack
		self.assertFalse(HoldingRack.objects.filter(holding_rack_id='HH12345679'))
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'PP12345678'}), {
			'holding': [''], 'holding_rack_id': 'HH12345679'}, follow=True)
		self.assertContains(response, 'Samples awaiting well assignment')
		self.assertContains(response, 'HH12345679')
		self.assertTrue(HoldingRack.objects.filter(holding_rack_id='HH12345679'))

	def test_rack_scanner(self):
		gel_1004 = Gel1004Csv.objects.get(filename='test1004.csv')
		# scanned the receiveing rack
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}), {
			'rack-scanner': ['']}, follow=True)
		self.assertContains(response, 'not found')

	def test_ready_and_reopen(self):
		gel_1004 = Gel1004Csv.objects.get(filename='test1004.csv')
		holding_rack = HoldingRack.objects.get(holding_rack_id='HH12345678')
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}), {
			'ready': holding_rack.pk}, follow=True)
		self.assertContains(response, 'Buffer will need to be added to the following wells')
		self.assertTrue(HoldingRackWell.objects.filter(holding_rack=holding_rack, buffer_added = True))
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}), {
			'reopen-rack': holding_rack.pk}, follow=True)
		self.assertFalse(HoldingRackWell.objects.filter(holding_rack=holding_rack, buffer_added = True))

	def test_sample(self):
		gel_1004 = Gel1004Csv.objects.get(filename='test1004.csv')
		# not found in receiving rack
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}), {
			'sample': [''], 'lab_sample_id':'1234567896'}, follow=True)
		self.assertContains(response, 'not found in GLH Rack')
		# added to holding rack
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}), {
			'sample': [''], 'lab_sample_id':'1234567890', 'well': ['']}, follow=True)
		self.assertContains(response, 'assigned to well B01')
		# wrong sample type
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}), {
			'sample': [''], 'lab_sample_id':'1234567897', 'well': ['']}, follow=True)
		self.assertContains(response, 'Sample does not match holding rack type!')
		# assign with sample from problem plate
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'PP12345678', 'holding_rack_id': 'HH12345678'}), {
			'sample': [''], 'lab_sample_id':'1234567893', 'well': ['']}, follow=True)
		self.assertContains(response, 'assigned to well C01')
		# wrong sample_delivery_mode
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH87654321'}), {
			'sample': [''], 'lab_sample_id': '1234567897', 'well': ['']}, follow=True)
		self.assertContains(response,
							'No matching germline sample found for this sample. Unable to assign to holding rack.')
		# correct sample_delivery_mode 'Tumour First'
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH87654321'}), {
			'sample': [''], 'lab_sample_id': '1234567689', 'well': ['']}, follow=True)
		self.assertContains(response,'assigned to well A01')

	def test_log_issue_normal(self):
		gel_1004 = Gel1004Csv.objects.get(filename='test1004.csv')
		sample = Sample.objects.get(laboratory_sample_id='1234567890')
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'SA12345678', 'gel1004': gel_1004.pk}), {
			'log-issue': sample.pk, 'comment': 'issue identified'}, follow=True)
		sample = Sample.objects.get(laboratory_sample_id='1234567890')
		self.assertTrue(sample.issue_identified)
		self.assertEqual(sample.issue_outcome, 'Not resolved')

	def test_log_issue_normal_on_holding_rack_page(self):
		gel_1004 = Gel1004Csv.objects.get(filename='test1004.csv')
		sample = Sample.objects.get(laboratory_sample_id='1234567890')
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'SA12345678', 'gel1004': gel_1004.pk, 'holding_rack_id': 'HH12345678'}), {
			'log-issue': sample.pk, 'comment': 'issue identified'}, follow=True)
		sample = Sample.objects.get(laboratory_sample_id='1234567890')
		self.assertTrue(sample.issue_identified)
		self.assertEqual(sample.issue_outcome, 'Not resolved')

	def test_log_issue_problem(self):
		sample = Sample.objects.get(laboratory_sample_id='1234567890')
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'PP12345678'}), {
			'log-issue': sample.pk, 'comment': 'issue identified'}, follow=True)
		sample = Sample.objects.get(laboratory_sample_id='1234567890')
		self.assertTrue(sample.issue_identified)
		self.assertEqual(sample.issue_outcome, 'Not resolved')

	def test_log_issue_problem_on_holding_rack_page(self):
		sample = Sample.objects.get(laboratory_sample_id='1234567890')
		response = self.client.post(reverse(assign_samples_to_holding_rack, kwargs={
			'rack': 'PP12345678', 'holding_rack_id': 'HH12345678'}), {
			'log-issue': sample.pk, 'comment': 'issue identified'}, follow=True)
		sample = Sample.objects.get(laboratory_sample_id='1234567890')
		self.assertTrue(sample.issue_identified)
		self.assertEqual(sample.issue_outcome, 'Not resolved')

class HoldingRackTestCase(TestCase):
	def setUp(self):
		holding_rack_rows = ['A','B','C','D','E','F','G','H']
		holding_rack_columns = ['01','02','03','04','05','06','07','08','09','10','11','12']
		self.client = Client()
		self.username = 'testuser'
		self.password = 'testing12345'
		self.user = User.objects.create_user(username=self.username, password=self.password)
		self.user.save()
		self.login = self.client.login(username=self.username, password=self.password)
		gel_1005_csv = Gel1005Csv.objects.create(filename='test1005.csv',
			report_generated_datetime=datetime.now(pytz.timezone('UTC')))
		gel_1004_csv = Gel1004Csv.objects.create(filename='test1004.csv', gel_1005_csv=gel_1005_csv,
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
			holding_rack = holding_rack,
			well_id = 'A01')
		holding_rack_well_three.sample = sample_six
		holding_rack_well_three.save()
		holding_rack_well_four = HoldingRackWell.objects.get(
			holding_rack = holding_rack,
			well_id = 'E01')
		holding_rack_well_four.sample = sample_seven
		holding_rack_well_four.save()
		problem_holding_rack = HoldingRack.objects.create(holding_rack_id='PP12345678',
			holding_rack_type='Problem')

	def test_load_holding_racks(self):
		response = self.client.get(reverse(holding_racks))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'platerplotter/holding-racks.html')
		self.assertContains(response, 'View current holding racks')
		self.assertContains(response, 'HH12345678')

	def test_load_holding_racks_with_holding_rack(self):
		response = self.client.get(reverse(holding_racks, kwargs={
			'holding_rack_id': 'HH12345678'}))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'platerplotter/holding-racks.html')
		self.assertContains(response, 'Holding rack')
		self.assertContains(response, 'HH12345678')

	def test_holding(self):
		response = self.client.post(reverse(holding_racks), {
			'holding': [''], 'holding_rack_id': 'SA12345678'}, follow=True)
		self.assertContains(response, 'You have scanned an active receiving rack')
		# scanned a problem holding rack
		response = self.client.post(reverse(holding_racks), {
			'holding': [''], 'holding_rack_id': 'PP12345678'}, follow=True)
		self.assertContains(response, 'You have scanned a holding rack being used for Problem samples')
		# scanned existing holding rack
		response = self.client.post(reverse(holding_racks), {
			'holding': [''], 'holding_rack_id': 'HH12345678'}, follow=True)
		self.assertContains(response, 'Holding rack')
		self.assertContains(response, 'HH12345678')
		# scanned non existant holding rack
		self.assertFalse(HoldingRack.objects.filter(holding_rack_id='HH12345679'))
		response = self.client.post(reverse(holding_racks), {
			'holding': [''], 'holding_rack_id': 'HH12345679'}, follow=True)
		self.assertContains(response, 'Holding rack not found with ID')

	def test_rack_scanner(self):
		response = self.client.post(reverse(holding_racks, kwargs={
			'holding_rack_id': 'HH12345678'}), {
			'rack-scanner': ['']}, follow=True)
		self.assertContains(response, 'not found')

	def test_ready_and_reopen(self):
		holding_rack = HoldingRack.objects.get(holding_rack_id='HH12345678')
		response = self.client.post(reverse(holding_racks, kwargs={
			'holding_rack_id': 'HH12345678'}), {
			'ready': holding_rack.pk}, follow=True)
		self.assertContains(response, 'Buffer will need to be added to the following wells')
		self.assertTrue(HoldingRackWell.objects.filter(holding_rack=holding_rack, buffer_added = True))
		response = self.client.post(reverse(holding_racks, kwargs={
			'holding_rack_id': 'HH12345678'}), {
			'reopen-rack': holding_rack.pk}, follow=True)
		self.assertFalse(HoldingRackWell.objects.filter(holding_rack=holding_rack, buffer_added = True))

	def test_log_issue(self):
		sample = Sample.objects.get(laboratory_sample_id='1234567890')
		response = self.client.post(reverse(holding_racks, kwargs={
			'holding_rack_id': 'HH12345678'}), {
			'log-issue': sample.pk, 'comment': 'issue identified'}, follow=True)
		sample = Sample.objects.get(laboratory_sample_id='1234567890')
		self.assertTrue(sample.issue_identified)
		self.assertEqual(sample.issue_outcome, 'Not resolved')

class ReadyToPlateAndPlateHoldingRackTestCase(TestCase):
	def setUp(self):
		holding_rack_rows = ['A','B','C','D','E','F','G','H']
		holding_rack_columns = ['01','02','03','04','05','06','07','08','09','10','11','12']
		self.client = Client()
		self.username = 'testuser'
		self.password = 'testing12345'
		self.user = User.objects.create_user(username=self.username, password=self.password)
		self.user.save()
		self.login = self.client.login(username=self.username, password=self.password)
		gel_1005_csv = Gel1005Csv.objects.create(filename='test1005.csv',
			report_generated_datetime=datetime.now(pytz.timezone('UTC')))
		gel_1004_csv = Gel1004Csv.objects.create(filename='test1004.csv', gel_1005_csv=gel_1005_csv,
			plating_organisation='wwm', report_received_datetime=datetime.now(pytz.timezone('UTC')))
		self.gel_1004_pk = gel_1004_csv.pk
		receiving_rack = ReceivingRack.objects.create(gel_1004_csv=gel_1004_csv,
			receiving_rack_id='SA12345678', laboratory_id='now', 
			glh_sample_consignment_number='abc-1234-12-12-12-1',
			rack_acknowledged=False, disease_area='Rare Disease',
			rack_type='Proband', priority='Routine')
		holding_rack = HoldingRack.objects.create(holding_rack_id='HH12345678',
			ready_to_plate = True)
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
			holding_rack = holding_rack,
			well_id = 'A01')
		holding_rack_well_three.sample = sample_six
		holding_rack_well_three.save()
		holding_rack_well_four = HoldingRackWell.objects.get(
			holding_rack = holding_rack,
			well_id = 'E01')
		holding_rack_well_four.sample = sample_seven
		holding_rack_well_four.save()

	def test_ready_to_plate(self):
		response = self.client.get(reverse(ready_to_plate))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'platerplotter/ready-to-plate.html')
		self.assertContains(response, 'Samples ready for plating')
		self.assertContains(response, 'HH12345678')

	def test_plate_holding_rack(self):
		holding_rack = HoldingRack.objects.get(holding_rack_id='HH12345678')
		response = self.client.get(reverse(plate_holding_rack, kwargs={
			'holding_rack_pk': holding_rack.pk}))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'platerplotter/plate-holding-rack.html')
		self.assertContains(response, 'Plate samples')
		self.assertContains(response, 'HH12345678')

	def test_rack_scanner(self):
		holding_rack = HoldingRack.objects.get(holding_rack_id='HH12345678')
		response = self.client.post(reverse(plate_holding_rack, kwargs={
			'holding_rack_pk': holding_rack.pk}), {
			'rack-scanner': ['']}, follow=True)
		self.assertContains(response, 'not found')

	def test_assign_plate(self):
		holding_rack = HoldingRack.objects.get(holding_rack_id='HH12345678')
		response = self.client.post(reverse(holding_racks, kwargs={
			'holding_rack_id': 'HH12345678'}), {
			'ready': holding_rack.pk}, follow=True)
		self.assertContains(response, 'Buffer will need to be added to the following wells')
		response = self.client.post(reverse(plate_holding_rack, kwargs={
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

class ReadyToDispatchAndAuditTestCase(TestCase):
	def setUp(self):
		holding_rack_rows = ['A','B','C','D','E','F','G','H']
		holding_rack_columns = ['01','02','03','04','05','06','07','08','09','10','11','12']
		self.client = Client()
		self.username = 'testuser'
		self.password = 'testing12345'
		self.user = User.objects.create_user(username=self.username, password=self.password)
		self.user.save()
		self.login = self.client.login(username=self.username, password=self.password)
		gel_1005_csv = Gel1005Csv.objects.create(filename='test1005.csv',
			report_generated_datetime=datetime.now(pytz.timezone('UTC')))
		gel_1004_csv = Gel1004Csv.objects.create(filename='test1004.csv', gel_1005_csv=gel_1005_csv,
			plating_organisation='wwm', report_received_datetime=datetime.now(pytz.timezone('UTC')))
		self.gel_1004_pk = gel_1004_csv.pk
		receiving_rack = ReceivingRack.objects.create(gel_1004_csv=gel_1004_csv,
			receiving_rack_id='SA12345678', laboratory_id='now', 
			glh_sample_consignment_number='abc-1234-12-12-12-1',
			rack_acknowledged=False, disease_area='Rare Disease',
			rack_type='Proband', priority='Routine')

		plate = Plate.objects.create(plate_id = 'LP0000000-DNA')
		holding_rack = HoldingRack.objects.create(holding_rack_id='HH12345678',
			disease_area='Rare Disease', holding_rack_type='Proband', priority='Routine',
			ready_to_plate = True, positions_confirmed=True)
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
			tissue_type='Normal or Germline sample', sample_received=True,
			sample_matched=True)
		sample_seven = Sample.objects.create(receiving_rack=receiving_rack,
			receiving_rack_well='G01', participant_id='p12345678907',
			group_id='r12345678907', priority='Routine',
			disease_area='Rare Disease', sample_type='Proband',
			clin_sample_type='dna_saliva', laboratory_sample_id='1234567896',
			uid='1234567896',
			laboratory_sample_volume=10, is_proband=True, is_repeat='New',
			tissue_type='Normal or Germline sample', sample_received=True,
			sample_matched=True)
		holding_rack_well_three = HoldingRackWell.objects.get(
			holding_rack = holding_rack,
			well_id = 'A01')
		holding_rack_well_three.sample = sample_six
		holding_rack_well_three.save()
		holding_rack_well_four = HoldingRackWell.objects.get(
			holding_rack = holding_rack,
			well_id = 'E01')
		holding_rack_well_four.sample = sample_seven
		holding_rack_well_four.save()
		self.client.post(reverse(holding_racks, kwargs={
			'holding_rack_id': 'HH12345678'}), {
			'ready': holding_rack.pk})
		holding_rack.plate = plate
		holding_rack.save()

		plate_two = Plate.objects.create(plate_id = 'LP0000001-DNA')
		holding_rack_two = HoldingRack.objects.create(holding_rack_id='HH12345679',
			disease_area='Rare Disease', holding_rack_type='Family', priority='Routine',
			ready_to_plate = True, positions_confirmed=True)
		for holding_rack_row in holding_rack_rows:
			for holding_rack_column in holding_rack_columns:
				HoldingRackWell.objects.create(holding_rack=holding_rack_two,
					well_id=holding_rack_row + holding_rack_column)
		sample_eight = Sample.objects.create(receiving_rack=receiving_rack,
			receiving_rack_well='A02', participant_id='p12345678908',
			group_id='r12345678906', priority='Routine',
			disease_area='Rare Disease', sample_type='Family',
			clin_sample_type='dna_saliva', laboratory_sample_id='1234567897',
			uid='1234567897',
			laboratory_sample_volume=10, is_proband=False, is_repeat='New',
			tissue_type='Normal or Germline sample', sample_received=True,
			sample_matched=True)
		sample_nine = Sample.objects.create(receiving_rack=receiving_rack,
			receiving_rack_well='B02', participant_id='p12345678909',
			group_id='r12345678906', priority='Routine',
			disease_area='Rare Disease', sample_type='Family',
			clin_sample_type='dna_saliva', laboratory_sample_id='1234567898',
			uid='1234567898',
			laboratory_sample_volume=10, is_proband=False, is_repeat='New',
			tissue_type='Normal or Germline sample', sample_received=True,
			sample_matched=True)
		holding_rack_well_five = HoldingRackWell.objects.get(
			holding_rack = holding_rack_two,
			well_id = 'A01')
		holding_rack_well_five.sample = sample_eight
		holding_rack_well_five.save()
		holding_rack_well_six = HoldingRackWell.objects.get(
			holding_rack = holding_rack_two,
			well_id = 'B01')
		holding_rack_well_six.sample = sample_nine
		holding_rack_well_six.save()
		self.client.post(reverse(holding_racks, kwargs={
			'holding_rack_id': 'HH12345679'}), {
			'ready': holding_rack_two.pk})
		holding_rack_two.plate = plate_two
		holding_rack_two.save()

		plate_three = Plate.objects.create(plate_id = 'LP0000002-DNA')
		holding_rack_three = HoldingRack.objects.create(holding_rack_id='HH12345680',
			disease_area='Cancer', holding_rack_type='Cancer Germline', priority='Routine',
			ready_to_plate = True, positions_confirmed=True)
		for holding_rack_row in holding_rack_rows:
			for holding_rack_column in holding_rack_columns:
				HoldingRackWell.objects.create(holding_rack=holding_rack_three,
					well_id=holding_rack_row + holding_rack_column)
		sample_ten = Sample.objects.create(receiving_rack=receiving_rack,
			receiving_rack_well='B03', participant_id='p12345678910',
			group_id='r12345678908', priority='Routine',
			disease_area='Cancer', sample_type='Cancer Germline',
			clin_sample_type='dna_saliva', laboratory_sample_id='1234567899',
			uid='1234567899',
			laboratory_sample_volume=10, is_proband=True, is_repeat='New',
			tissue_type='Normal or Germline sample', sample_received=True,
			sample_matched=True)
		sample_eleven = Sample.objects.create(receiving_rack=receiving_rack,
			receiving_rack_well='B04', participant_id='p12345678911',
			group_id='r12345678909', priority='Routine',
			disease_area='Cancer', sample_type='Cancer Germline',
			clin_sample_type='dna_saliva', laboratory_sample_id='1234567900',
			uid='1234567900',
			laboratory_sample_volume=10, is_proband=True, is_repeat='New',
			tissue_type='Normal or Germline sample', sample_received=True,
			sample_matched=True)
		holding_rack_well_seven = HoldingRackWell.objects.get(
			holding_rack = holding_rack_three,
			well_id = 'A01')
		holding_rack_well_seven.sample = sample_ten
		holding_rack_well_seven.save()
		holding_rack_well_eight = HoldingRackWell.objects.get(
			holding_rack = holding_rack_three,
			well_id = 'D01')
		holding_rack_well_eight.sample = sample_eleven
		holding_rack_well_eight.save()
		self.client.post(reverse(holding_racks, kwargs={
			'holding_rack_id': 'HH12345680'}), {
			'ready': holding_rack_three.pk})
		holding_rack_three.plate = plate_three
		holding_rack_three.save()

		plate_four = Plate.objects.create(plate_id = 'LP0000003-DNA')
		holding_rack_four = HoldingRack.objects.create(holding_rack_id='HH12345681',
			disease_area='Cancer', holding_rack_type='Tumour', priority='Routine',
			ready_to_plate = True, positions_confirmed=True)
		for holding_rack_row in holding_rack_rows:
			for holding_rack_column in holding_rack_columns:
				HoldingRackWell.objects.create(holding_rack=holding_rack_four,
					well_id=holding_rack_row + holding_rack_column)
		sample_twelve = Sample.objects.create(receiving_rack=receiving_rack,
			receiving_rack_well='B07', participant_id='p12345678911',
			group_id='r12345678909', priority='Routine',
			disease_area='Cancer', sample_type='Tumour',
			clin_sample_type='dna_saliva', laboratory_sample_id='1234567901',
			uid='1234567901',
			laboratory_sample_volume=10, is_proband=True, is_repeat='New',
			tissue_type='Solid tumour sample', sample_received=True,
			sample_matched=True)
		sample_thirteen = Sample.objects.create(receiving_rack=receiving_rack,
			receiving_rack_well='B08', participant_id='p12345678911',
			group_id='r12345678909', priority='Routine',
			disease_area='Cancer', sample_type='Tumour',
			clin_sample_type='dna_saliva', laboratory_sample_id='1234567902',
			uid='1234567902',
			laboratory_sample_volume=10, is_proband=True, is_repeat='New',
			tissue_type='Solid tumour sample', sample_received=True,
			sample_matched=True)
		holding_rack_well_nine = HoldingRackWell.objects.get(
			holding_rack = holding_rack_four,
			well_id = 'A01')
		holding_rack_well_nine.sample = sample_twelve
		holding_rack_well_nine.save()
		holding_rack_well_ten = HoldingRackWell.objects.get(
			holding_rack = holding_rack_four,
			well_id = 'B01')
		holding_rack_well_ten.sample = sample_thirteen
		holding_rack_well_ten.save()
		self.client.post(reverse(holding_racks, kwargs={
			'holding_rack_id': 'HH12345681'}), {
			'ready': holding_rack_four.pk})
		holding_rack_four.plate = plate_four
		holding_rack_four.save()

	def test_ready_to_dispatch(self):
		response = self.client.get(reverse(ready_to_dispatch))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'platerplotter/ready-to-dispatch.html')
		self.assertContains(response, 'Plates ready for dispatch')
		self.assertContains(response, 'LP0000000-DNA')

	def test_generate_gel1008_no_plates(self):
		response = self.client.post(reverse(ready_to_dispatch, kwargs={
			'test_status': True}), {
			'generate-manifests': [''], 'selected_plate': [], 'consignment_number': '1234567890',
			'date_of_dispatch': date.today()}, follow=True)
		self.assertContains(response, 'No plates selected!')

	def test_generate_gel1008_all_plates(self):
		plate_list_pk = []
		plate_list_pk.append(Plate.objects.get(plate_id = 'LP0000000-DNA').pk)
		plate_list_pk.append(Plate.objects.get(plate_id = 'LP0000001-DNA').pk)
		plate_list_pk.append(Plate.objects.get(plate_id = 'LP0000002-DNA').pk)
		plate_list_pk.append(Plate.objects.get(plate_id = 'LP0000003-DNA').pk)
		response = self.client.post(reverse(ready_to_dispatch, kwargs={
			'test_status': True}), {
			'generate-manifests': [''], 'selected_plate': plate_list_pk, 'consignment_number': '1234567890',
			'date_of_dispatch': date.today()}, follow=True)
		self.assertContains(response, 'GEL1008 messages have been generated for the following consignment manifests')
		directory = str(Path.cwd().parent) + '/TestData/Outbound/'
		self.assertEqual(len(os.listdir(directory + 'ConsignmentManifests/')), 4)
		self.assertEqual(len(os.listdir(directory + 'GEL1008/')), 4)
		files = glob.glob(directory + 'ConsignmentManifests/' + '*')
		for f in files:
			os.remove(f)
		files = glob.glob(directory + 'GEL1008/' + '*')
		for f in files:
			os.remove(f)
		directory = str(Path.cwd().parent) + '/TestData/Outbound/ConsignmentManifests/'
		self.assertEqual(len(os.listdir(directory)), 0)
		directory = str(Path.cwd().parent) + '/TestData/Outbound/GEL1008/'
		self.assertEqual(len(os.listdir(directory)), 0)

	def test_generate_gel1008_not_all_plates(self):
		plate_list_pk = []
		plate_list_pk.append(Plate.objects.get(plate_id = 'LP0000000-DNA').pk)
		plate_list_pk.append(Plate.objects.get(plate_id = 'LP0000003-DNA').pk)
		response = self.client.post(reverse(ready_to_dispatch, kwargs={
			'test_status': True}), {
			'generate-manifests': [''], 'selected_plate': plate_list_pk, 'consignment_number': '1234567890',
			'date_of_dispatch': date.today()}, follow=True)
		self.assertContains(response, 'All synchronous multi-tumour samples must be sent in the same consignment')
		self.assertContains(response, 'All family member samples must be sent in the same consignment')
		directory = str(Path.cwd().parent) + '/TestData/Outbound/ConsignmentManifests/'
		self.assertEqual(len(os.listdir(directory)), 0)

	def test_scan_plate(self):
		response = self.client.post(reverse(ready_to_dispatch), {
			'plate': [''], 'selected_plates': '', 'plate_id': 'LP0000004-DNA',
			'date_of_dispatch': date.today()}, follow=True)
		self.assertContains(response, 'not found in list of plates ready for dispatch')
		plate = Plate.objects.get(plate_id='LP0000003-DNA')
		response = self.client.post(reverse(ready_to_dispatch), {
			'plate': [''], 'selected_plates': ['1','2','3','4', plate.pk], 'plate_id': 'LP0000003-DNA',
			'date_of_dispatch': date.today()}, follow=True)
		self.assertContains(response, 'already selected for this consignment')
		response = self.client.post(reverse(ready_to_dispatch), {
			'plate': [''], 'selected_plates': '', 'plate_id': 'LP0000003-DNA',
			'date_of_dispatch': date.today()}, follow=True)
		self.assertContains(response, 'added to the consignment list')

	def test_audit(self):
		response = self.client.post(reverse(audit), {
			'search_term': '003-DN'}, follow=True)
		self.assertContains(response, 'LP0000003-DNA')