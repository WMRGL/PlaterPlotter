import re
import pytz
from django import forms
from django.forms import ModelForm
from datetime import datetime
from platerplotter.models import ReceivedSamples, ReceivedSample
from django.core.exceptions import ValidationError

class ReceivedSampleForm(ModelForm):
	class Meta:
		model = ReceivedSample
		exclude = ['sampleReceivedDateTime']

	def clean_gmcRackId(self):
		gmcRackId = self.cleaned_data['gmcRackId']
		if not re.match(r'^[A-Z]{2}\d{8}$', gmcRackId):
			raise ValidationError("Invalid: should be two letters followed by 8 digits")
		return gmcRackId

	def clean_laboratorySampleId(self):
		laboratorySampleId = self.cleaned_data['laboratorySampleId']
		if not re.match(r'^\d{10}$', laboratorySampleId):
			raise ValidationError("Invalid: should be 10 digits (left padded with 0's)")
		return laboratorySampleId

	def save(self, commit=True):
		instance = super(ReceivedSampleForm, self).save(commit=False)
		instance.sampleReceivedDateTime = datetime.now(pytz.timezone('Europe/London'))
		if commit:
			instance.save()
		return instance



class ReceivedSamplesForm(ModelForm):
	class Meta:
		model = ReceivedSamples
		exclude = ['sampleReceivedDateTime']

	def clean_gmcRackId(self):
		gmcRackId = self.cleaned_data['gmcRackId']
		if not re.match(r'^[A-Z]{2}\d{8}$', gmcRackId):
			raise ValidationError("Invalid rack ID.")
		return gmcRackId

	def clean_A1(self):
		a1 = self.cleaned_data['A1']
		if a1 != '':
			if not re.match(r'^\d{10}$', a1):
				raise ValidationError("Invalid")
		return a1

	def save(self, commit=True):
		instance = super(ReceivedSamplesForm, self).save(commit=False)
		instance.sampleReceivedDateTime = datetime.now(pytz.timezone('Europe/London'))
		if commit:
			instance.save()
		return instance
