import re
import pytz
from django import forms
from django.forms import ModelForm
from datetime import datetime
from platerplotter.models import Plate, Sample, Gel1008Csv
from django.core.exceptions import ValidationError
from django.utils import timezone

class HoldingRackForm(forms.Form):
	holding_rack_id = forms.CharField(label='', widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

	def clean_holding_rack_id(self):
		holding_rack_id = self.cleaned_data['holding_rack_id'].upper()
		if not re.match(r'^[A-Z]{2}\d{8}$', holding_rack_id):
			raise ValidationError("Invalid rack ID")
		else:
			return holding_rack_id.upper()


class PlateSelectForm(forms.Form):
	plate_id = forms.CharField(label='', widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

	def clean_plate_id(self):
		plate_id = self.cleaned_data['plate_id'].upper()
		if not re.match(r'^LP\d{7}-DNA$', plate_id):
			raise ValidationError("Invalid Plate ID")
		else:
			return plate_id.upper()

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
			return plate_id.upper()
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
			if not re.match(r'^.*$', consignment_number):
				raise ValidationError("Invalid consignment number")
			if ',' in consignment_number:
				raise ValidationError("Invalid consignment number, cannot contain ','.")
			return consignment_number
		else:
			raise ValidationError("Required field.")

	def clean_date_of_dispatch(self):
		if self.cleaned_data['date_of_dispatch']:
			date_of_dispatch = self.cleaned_data['date_of_dispatch']
			if date_of_dispatch <= timezone.now() - timezone.timedelta(days=1):
				raise forms.ValidationError("The date cannot be in the past")
			if date_of_dispatch > timezone.now() + timezone.timedelta(days=14):
				raise forms.ValidationError("The date must be within 2 weeks of today's date")
			return date_of_dispatch
		else:
			raise ValidationError("Required field.")