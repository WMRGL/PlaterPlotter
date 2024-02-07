from django import forms

from platerplotter.models import HoldingRack


class DiscardForm(forms.ModelForm):
	class Meta:
		model = HoldingRack
		fields = ['holding_rack_id', 'checked_by', 'discard_date', 'discarded_by', 'discarded']

