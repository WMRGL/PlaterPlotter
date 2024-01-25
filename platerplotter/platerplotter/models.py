from django.db import models
from django.contrib.auth.models import User

from notifications.models import Sample
from notifications.choices import well_ids


class Gel1008Csv(models.Model):
	filename = models.CharField(max_length=60)
	report_generated_datetime = models.DateTimeField()
	consignment_number = models.CharField(max_length=50, null=True, blank=True)
	date_of_dispatch = models.DateTimeField(null=True, blank=True)
	consignment_collected = models.BooleanField(default=False)

	def __str__(self):
		return self.filename

	class Meta:
		app_label = 'platerplotter'
		db_table = 'Gel1008Csv'
		verbose_name = 'Gel1008 CSV'
		verbose_name_plural = 'Gel1008 CSVs'

class Plate(models.Model):
	gel_1008_csv = models.ForeignKey(Gel1008Csv, on_delete=models.SET_NULL, null=True, blank=True, related_name='related_plate')
	plate_id = models.CharField(max_length=13, unique=True)

	def __str__(self):
		return self.plate_id

	class Meta:
		app_label = 'platerplotter'
		db_table = 'Plate'
		verbose_name = 'Plate'
		verbose_name_plural = 'Plates'

