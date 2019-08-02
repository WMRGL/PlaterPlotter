import re
import pytz
from django import forms
from django.forms import ModelForm
from datetime import datetime
from platerplotter.models import Plate, Sample, Gel1008Csv
from django.core.exceptions import ValidationError

class HoldingRackForm(forms.Form):
	holding_rack_id = forms.CharField(label='', widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

	def clean_holding_rack_id(self):
		holding_rack_id = self.cleaned_data['holding_rack_id']
		if not re.match(r'^[a-zA-Z]{2}\d{8}$', holding_rack_id):
			raise ValidationError("Invalid rack ID")
		else:
			return holding_rack_id.upper()

class SampleSelectForm(forms.Form):
	lab_sample_id = forms.CharField(label='', widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

	def clean_lab_sample_id(self):
		lab_sample_id = self.cleaned_data['lab_sample_id']
		if not re.match(r'^\d{10}$', lab_sample_id):
			raise ValidationError("Invalid Laboratory Sample ID")
		else:
			return lab_sample_id

class LogIssueForm(forms.ModelForm):
	class Meta:
		model = Sample
		fields = ('comment',)
		labels = {'comment': "",}
		widgets = {'comment': forms.Textarea(attrs={'rows':4, 'cols':50}),}

class ResolveIssueForm(forms.ModelForm):
	class Meta:
		model = Sample
		fields = ('comment', 
				'issue_outcome',)
		labels = {'comment': "", 
				'issue_outcome' : "Outcome",}
		widgets = {'comment': forms.Textarea(attrs={'rows':4, 'cols':50}),}

class PlatingForm(ModelForm):
	class Meta:
		model = Plate
		fields = ('plate_id',)
		labels = {
			'plate_id': "",
		}

	def clean_plate_id(self):
		if self.cleaned_data['plate_id']:
			plate_id = self.cleaned_data['plate_id'].upper()
			if Plate.objects.filter(plate_id=plate_id).exists():
				raise ValidationError("Plate ID already used.")
			if not re.match(r'^LP\d{7}-DNA$', plate_id):
				raise ValidationError("Invalid Plate ID.")
			return plate_id
		else:
			raise ValidationError("Required field.")

class Gel1008Form(ModelForm):
	class Meta:
		model = Gel1008Csv
		fields = ('consignment_number', 'date_of_dispatch')
		widgets = {
			'date_of_dispatch': forms.DateInput(attrs={'type': 'date','data-provide': 'datepicker'}),
		}
		labels = {
			'consignment_number': "Consignment Number",
			'date_of_dispatch': "Date of Dispatch"
		}

	def clean_consignment_number(self):
		if self.cleaned_data['consignment_number']:
			consignment_number = self.cleaned_data['consignment_number']
			if not re.match(r'^\d{10}$', consignment_number):
				raise ValidationError("Invalid consignment number")
			return consignment_number
		else:
			raise ValidationError("Required field.")

	def clean_date_of_dispatch(self):
		if self.cleaned_data['date_of_dispatch']:
			date_of_dispatch = self.cleaned_data['date_of_dispatch']
			return date_of_dispatch
		else:
			raise ValidationError("Required field.")