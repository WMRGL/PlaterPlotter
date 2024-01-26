from django.db import models

from notifications.choices import well_ids
from notifications.models import Sample
from ready.models import Gel1008Csv


# Create your models here.

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



