import re
import pytz
from django import forms
from django.forms import ModelForm
from datetime import datetime
from platerplotter.models import Gel1004Csv, Rack, Plate, Sample, Gel1008Csv
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

class ParticipantIdForm(forms.Form):
	participant_id = forms.CharField(label='', widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

	def clean_participant_id(self):
		participant_id = self.cleaned_data['participant_id'].lower()
		if not re.match(r'^[p,P]\d{2}-\d*$', participant_id):
			raise ValidationError("Invalid Participant ID")
		else:
			return participant_id


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
				print("error raised")
				raise ValidationError("Plate ID already used.")
			if not re.match(r'^LP\d{7}-DNA$', plate_id):
				print("error raised")
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


# class ReceivedSampleForm(ModelForm):
# 	class Meta:
# 		model = ReceivedSample
# 		exclude = ['sampleReceivedDateTime']

# 	def clean_gmcRackId(self):
# 		gmcRackId = self.cleaned_data['gmcRackId']
# 		if not re.match(r'^[A-Z]{2}\d{8}$', gmcRackId):
# 			raise ValidationError("Invalid: should be two letters followed by 8 digits")
# 		return gmcRackId

# 	def clean_laboratorySampleId(self):
# 		laboratorySampleId = self.cleaned_data['laboratorySampleId']
# 		if not re.match(r'^\d{10}$', laboratorySampleId):
# 			raise ValidationError("Invalid: should be 10 digits (left padded with 0's)")
# 		return laboratorySampleId

# 	def save(self, commit=True):
# 		instance = super(ReceivedSampleForm, self).save(commit=False)
# 		instance.sampleReceivedDateTime = datetime.now(pytz.timezone('Europe/London'))
# 		if commit:
# 			instance.save()
# 		return instance
