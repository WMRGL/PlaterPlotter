import re
from django import forms
from django.forms import ModelForm
from platerplotter.models import ReveivedSamples
from django.core.exceptions import ValidationError

class ReceivedSamplesForm(ModelForm):
	class Meta:
		model = ReveivedSamples
		exclude = ['sampleReceivedDateTime']

	def clean_gmcRackId(self):
		gmcRackId = self.cleaned_data['gmcRackId']
		if not re.match(r'^[A-Z]{2}\d{8}$', gmcRackId):
			raise ValidationError("Invalid rack ID.")
		return gmcRackId

	def clean_A1(self):
		a1 = self.cleaned_data['A1']
		if not re.match(r'^\d{10}$', a1):
			raise ValidationError("Invalid sample ID.")
		return a1
