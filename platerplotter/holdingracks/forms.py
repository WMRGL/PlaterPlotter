import re

from django import forms
from django.core.exceptions import ValidationError


class HoldingRackForm(forms.Form):
	holding_rack_id = forms.CharField(label='', widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

	def clean_holding_rack_id(self):
		holding_rack_id = self.cleaned_data['holding_rack_id'].upper()
		if not re.match(r'^[A-Z]{2}\d{8}$', holding_rack_id):
			raise ValidationError("Invalid rack ID")
		else:
			return holding_rack_id.upper()
