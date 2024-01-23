import re

from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django import forms

from notifications.models import Sample


class LogIssueForm(forms.ModelForm):
	class Meta:
		model = Sample
		fields = ('comment',)
		labels = {'comment': "", }
		widgets = {'comment': forms.Textarea(attrs={'rows': 4, 'cols': 50}), }


class ResolveIssueForm(forms.ModelForm):
	class Meta:
		model = Sample
		fields = ('comment', 'issue_outcome',)
		labels = {'comment': "", 'issue_outcome': "Outcome", }
		widgets = {'comment': forms.Textarea(attrs={'rows': 4, 'cols': 50}), }


class SampleSelectForm(forms.Form):
	lab_sample_id = forms.CharField(label='', widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

	def clean_lab_sample_id(self):
		lab_sample_id = self.cleaned_data['lab_sample_id']
		if not re.match(r'^\d{10}$', lab_sample_id):
			raise ValidationError("Invalid Laboratory Sample ID")
		else:
			return lab_sample_id
