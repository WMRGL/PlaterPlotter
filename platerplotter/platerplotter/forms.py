from django import forms
from django.forms import ModelForm
from platerplotter.models import ReveivedSamples
from django.core.exceptions import ValidationError

class ReceivedSamplesForm(ModelForm):
	class Meta:
		model = ReveivedSamples
		exclude = ['sampleReceivedDateTime']