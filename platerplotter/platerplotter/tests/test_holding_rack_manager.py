from django.test import TestCase
from platerplotter.holding_rack_manager import *
from platerplotter.models import *

class HoldingRackManagerTestCase(TestCase):
	def setUp(self):
		self.hr = HoldingRack(holding_rack_id='AB12345678')
		self.hrm = HoldingRackManager(self.hr)
	
	def test_lookup_alt_index(self):
		self.assertEqual(self.hrm.lookup_alt_index(1), 12)

	def test_lookup_new_indices(self):
		self.assertEqual(self.hrm.lookup_new_indices([0,1,2]), [0,8,16])

	def test_determine_indices_to_avoid(self):
		self.assertEqual(set(self.hrm.determine_indices_to_avoid(0)),set([0,8,16,24,32,
			40,48,56,64,72,80,88,1,9,17,2,10,18,3,11,19]))
		self.assertEqual(set(self.hrm.determine_indices_to_avoid(25)),set([1,9,17,25,
			33,41,49,57,65,73,81,89,8,16,24,32,40,10,18,26,34,42,
			11,19,27,35,43,12,20,28,36,44]))