import pytz
from django.test import TestCase
from django.utils import timezone
from datetime import datetime
from platerplotter.models import Plate
from platerplotter.forms import (HoldingRackForm, PlatingForm,
	Gel1008Form, LogIssueForm, ResolveIssueForm, PlateSelectForm)
from problemsamples.forms import SampleSelectForm


class FormTestCase(TestCase):
	def setUp(self):
 		self.plate = Plate.objects.create(plate_id='LP1234568-DNA')

	def test_holding_rack_form(self):
		form = HoldingRackForm(data={'holding_rack_id': 'AZ12345678'})
		self.assertTrue(form.is_valid())
		form = HoldingRackForm(data={'holding_rack_id': 'A123456789'})
		self.assertFalse(form.is_valid())

	def test_sample_select_form(self):
		form = SampleSelectForm(data={'lab_sample_id': '1234567890'})
		self.assertTrue(form.is_valid())
		form = SampleSelectForm(data={'lab_sample_id': '123456789'})
		self.assertFalse(form.is_valid())

	def test_plate_select_form(self):
		form = PlateSelectForm(data={'plate_id': 'LP1234567-DNA'})
		self.assertTrue(form.is_valid())
		form = PlateSelectForm(data={'plate_id': 'LP1234567DNA'})
		self.assertFalse(form.is_valid())

	def test_log_issue_form(self):
		form = LogIssueForm(data={'comment': 'issue comment'})
		self.assertTrue(form.is_valid())

	def test_resolve_issue_form(self):
		form = ResolveIssueForm(data={'comment': 'issue resolved',
				'issue_outcome': 'Ready for plating'})
		self.assertTrue(form.is_valid())

	def test_plating_form(self):
		form = PlatingForm(data={'plate_id': 'LP1234567-DNA'})
		self.assertTrue(form.is_valid())
		form = PlatingForm(data={'plate_id': 'LP1234568-DNA'})
		self.assertFalse(form.is_valid())
		form = PlatingForm(data={'plate_id': 'LP1234567DNA'})
		self.assertFalse(form.is_valid())
		form = PlatingForm(data={})
		self.assertFalse(form.is_valid())
		form = PlatingForm(data={'plate_id': None})
		self.assertFalse(form.is_valid())

	def test_gel1008_form(self):
		date = datetime.now(pytz.timezone('UTC'))
		form = Gel1008Form(data={'consignment_number': '1234567890',
			'date_of_dispatch': date})
		self.assertTrue(form.is_valid())
		form = Gel1008Form(data={'consignment_number': None,
			'date_of_dispatch': date})
		self.assertFalse(form.is_valid())
		date = datetime.now(pytz.timezone('UTC')) - timezone.timedelta(days=1)
		form = Gel1008Form(data={'consignment_number': '1234567890',
			'date_of_dispatch': date})
		self.assertFalse(form.is_valid())
		date = datetime.now(pytz.timezone('UTC')) + timezone.timedelta(days=15)
		form = Gel1008Form(data={'consignment_number': '1234567890',
			'date_of_dispatch': date})
		self.assertFalse(form.is_valid())
		date = datetime.now(pytz.timezone('UTC')) + timezone.timedelta(days=15)
		form = Gel1008Form(data={'consignment_number': '1234567890',
			'date_of_dispatch': None})
		self.assertFalse(form.is_valid())