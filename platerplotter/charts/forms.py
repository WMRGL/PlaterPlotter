from django import forms


class DateRangeForm(forms.Form):
    start = forms.DateField(input_formats=['%Y-%m-%d'], required=True)
    end = forms.DateField(input_formats=['%Y-%m-%d'], required=True)
