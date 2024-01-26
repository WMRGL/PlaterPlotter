from django.db import models

# Create your models here.


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

