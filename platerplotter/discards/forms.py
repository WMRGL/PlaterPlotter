from django import forms
from django.contrib.auth.models import User  # or your custom user model

from .models import Discard


class DiscardForm(forms.ModelForm):
	class Meta:
		model = Discard
		fields = ['holding_rack', 'checked_by', 'dispatch_date', 'discarded_by']

	def __init__(self, *args, **kwargs):
		current_user = kwargs.pop('current_user', None)
		super().__init__(*args, **kwargs)
		print(current_user)

		# Set the queryset for discarded_by to include only the current user
		if current_user:
			self.fields['discarded_by'].queryset = User.objects.filter(pk=current_user.pk)
		else:
			self.fields['discarded_by'].queryset = User.objects.none()
