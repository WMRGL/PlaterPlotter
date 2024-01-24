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

class HoldingRack(models.Model):
	plate = models.OneToOneField(Plate, on_delete=models.CASCADE, null=True, blank=True, related_name='holding_rack')
	holding_rack_id = models.CharField(max_length=11)
	disease_area = models.CharField(max_length=12, choices = (
			("Cancer", "Cancer"),
			("Rare Disease", "Rare Disease"),
			("Unassigned", "Unassigned")), default="Unassigned")
	holding_rack_type = models.CharField(max_length=15, choices=(("Proband", "Proband"),
		("Family", "Family"), ("Cancer Germline", "Cancer Germline"),
		("Tumour", "Tumour"), ("Problem", "Problem"), ("Unassigned", "Unassigned")), default="Unassigned")
	priority = models.CharField(max_length=10, choices=(("Routine", "Routine"),
		("Urgent", "Urgent"),
		("Unassigned", "Unassigned")), default="Unassigned")
	half_full = models.BooleanField(default=False)
	full = models.BooleanField(default=False)
	ready_to_plate = models.BooleanField(default=False)
	positions_confirmed = models.BooleanField(default=False)

	def __str__(self):
		return "Holding Rack ID: " + self.holding_rack_id

	class Meta:
		app_label = 'platerplotter'
		db_table = 'HoldingRack'
		verbose_name = 'Holding rack'
		verbose_name_plural = 'Holding racks'


class HoldingRackWell(models.Model):
	holding_rack = models.ForeignKey(HoldingRack, on_delete=models.CASCADE, related_name = 'wells')
	well_id = models.CharField(max_length=3, choices=well_ids)
	buffer_added = models.BooleanField(default=False)
	sample = models.OneToOneField(Sample, on_delete=models.SET_NULL, null=True, blank=True, related_name='holding_rack_well')

	def __str__(self):
		return self.holding_rack.holding_rack_id + ' ' + self.well_id

	class Meta:
		app_label = 'platerplotter'
		db_table = 'HoldingRackWell'
		verbose_name = 'Holding rack well'
		verbose_name_plural = 'Holding rack wells'

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