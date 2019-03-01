import re
import pytz
from django import forms
from django.forms import ModelForm
from datetime import datetime
from platerplotter.models import Gel1004Csv, Rack, Plate, Sample
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
			print("error raised")
			raise ValidationError("Invalid Laboratory Sample ID")
		else:
			return lab_sample_id

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
