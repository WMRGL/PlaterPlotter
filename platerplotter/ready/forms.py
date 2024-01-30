import re
from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils import timezone


from platerplotter.models import Gel1008Csv


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


