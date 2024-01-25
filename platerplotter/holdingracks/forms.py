import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Plate


class HoldingRackForm(forms.Form):
	holding_rack_id = forms.CharField(label='', widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

	def clean_holding_rack_id(self):
		holding_rack_id = self.cleaned_data['holding_rack_id'].upper()
		if not re.match(r'^[A-Z]{2}\d{8}$', holding_rack_id):
			raise ValidationError("Invalid rack ID")
		else:
			return holding_rack_id.upper()



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
