from django.db import models

from notifications.choices import well_ids
# Create your models here.


class RackScanner(models.Model):
	filename = models.CharField(max_length=60)
	scanned_id = models.CharField(max_length=13)
	date_modified = models.DateTimeField()
	acknowledged = models.BooleanField(default=False)

	class Meta:
		unique_together = (('filename', 'scanned_id', 'date_modified'),)
		app_label = 'platerplotter'
		db_table = 'RackScanner'
		verbose_name = 'Rack scanner'
		verbose_name_plural = 'Rack scanners'

	def __str__(self):
		return self.filename + ' ' + str(self.date_modified)


class RackScannerSample(models.Model):
	rack_scanner = models.ForeignKey(RackScanner, on_delete=models.CASCADE)
	sample_id = models.CharField(max_length=10)
	position = models.CharField(max_length=3, choices=well_ids)
	matched = models.BooleanField(default=False)

	class Meta:
		unique_together = (('rack_scanner', 'sample_id', 'position'))
		app_label = 'platerplotter'
		db_table = 'RackScannerSample'
		verbose_name = 'Rack scanner sample'
		verbose_name_plural = 'Rack scanner samples'

	def __str__(self):
		return self.rack_scanner.scanned_id + ': ' + self.sample_id