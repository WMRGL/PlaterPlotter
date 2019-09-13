from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from platerplotter.views import *
from platerplotter.models import *
import os

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
		rack_scan(test_status=True)
		self.assertEqual(RackScanner.objects.count(), 1)
		self.assertEqual(RackScannerSample.objects.count(), 4)
		os.rename(str(Path.cwd().parent) + '/TestData/Inbound/RackScanner/processed/rack_scan_test_file.csv',
			str(Path.cwd().parent) + '/TestData/Inbound/RackScanner/rack_scan_test_file.csv')
		rack_scan(test_status=True)
		self.assertEqual(RackScanner.objects.count(), 1)
		self.assertEqual(RackScannerSample.objects.count(), 4)
		os.rename(str(Path.cwd().parent) + '/TestData/Inbound/RackScanner/processed/rack_scan_test_file.csv',
			str(Path.cwd().parent) + '/TestData/Inbound/RackScanner/rack_scan_test_file.csv')

	# def test_confirm_sample_positions(self):
	# 	c = Client()
	# 	request = c.get(reverse(import_acks))
	# 	print(request)
	# 	os.rename(str(Path.cwd().parent) + '/TestData/Inbound/RackScanner/processed/rack_scan_test_file.csv',
	# 		str(Path.cwd().parent) + '/TestData/Inbound/RackScanner/rack_scan_test_file.csv')

class ViewTestCase(TestCase):
	def setUp(self):
		self.client = Client()
		self.username = 'testuser'
		self.password = 'testing12345'
		self.user = User.objects.create_user(username=self.username, password=self.password)
		self.user.save()
		self.login = self.client.login(username=self.username, password=self.password)
		# sample = Sample.objects.create(nhs_number='1234567891', forename='HARRY', surname='POTTER',
		#								created_by=self.user,  updated_by=self.user)
		# hpo = HPO.objects.create(code='HP:0000001', label='All')
		# sample.hpo_terms.add(hpo)
		# metadata = Metadata.objects.create(metadata='test_metadata', title='Test Metadata')
		# SampleMetadata.objects.create(sample=sample, metadata=metadata, text='original')

	def test_login(self):
		self.assertTrue(self.login)

	def test_import_acks(self):
		response = self.client.get(reverse(import_acks))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'platerplotter/import-acks.html')
		self.assertContains(response, 'Unacknowledged Racks')
		response_post_import = self.client.post(reverse(import_acks, kwargs={'test_status': True}), {'import-1004': ['']})
		print("***********************************************************")
		print(response_post_import)
