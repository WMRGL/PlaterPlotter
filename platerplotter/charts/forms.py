from datetime import datetime

from django import forms


class DateRangeForm(forms.Form):
    start = forms.DateField(input_formats=['%Y-%m-%d'], required=True)
    end = forms.DateField(input_formats=['%Y-%m-%d'], required=True)


class MonthForm(forms.Form):
    month = forms.DateField(input_formats=['%Y-%m'], required=True)


class WeekForm(forms.Form):
    week = forms.CharField(required=True)

    def clean_week(self):
        week_str = self.cleaned_data['week']
        try:
            year, week = map(int, week_str.split('-W'))
            # Convert year and week number to a date (Monday of the given week)
            date = datetime.strptime(f'{year} {week} 1', '%G %V %u').date()
        except ValueError:
            raise forms.ValidationError('Invalid week format. Expected format is YYYY-Www.')
        return date
