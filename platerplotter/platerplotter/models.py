from django.db import models
from django.contrib.auth.models import User
from platerplotter.choices import well_ids, lab_ids, sample_types

class Gel1005Csv(models.Model):
	filename = models.CharField(max_length=60)
	report_generated_datetime = models.DateTimeField()

	def __str__(self):
		return self.filename

class Gel1004Csv(models.Model):
	gel_1005_csv = models.ForeignKey(Gel1005Csv, on_delete=models.CASCADE, null=True, blank=True)
	filename = models.CharField(max_length=60)
	plating_organisation = models.CharField(max_length=10, choices=lab_ids, default="wwm")
	report_received_datetime = models.DateTimeField()

	def __str__(self):
		return self.filename


class Gel1008Csv(models.Model):
	filename = models.CharField(max_length=60)
	report_generated_datetime = models.DateTimeField()
	consignment_number = models.CharField(max_length=10, null=True, blank=True)
	date_of_dispatch = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return self.filename

class Rack(models.Model):
	gel_1004_csv = models.ForeignKey(Gel1004Csv, on_delete=models.CASCADE)
	gmc_rack_id = models.CharField(max_length=12)
	laboratory_id = models.CharField(max_length=3, choices=lab_ids)
	rack_acknowledged = models.BooleanField(default=False)
	disease_area = models.CharField(max_length=12, choices = (
			("Cancer", "Cancer"),
			("Rare Disease", "Rare Disease"),
			("Mixed", "Mixed")), null=True, blank=True)
	plate_type = models.CharField(max_length=15, choices=(("Proband", "Proband"),
		("Family", "Family"), ("Cancer Germline", "Cancer Germline"),
		("Tumour", "Tumour"), ("Mixed", "Mixed")), null=True, blank=True)
	priority = models.CharField(max_length=10, choices=(("Routine", "Routine"),
		("Urgent", "Urgent"), ("Mixed", "Mixed")), null=True, blank=True)	

	def __str__(self):
		return self.gmc_rack_id

class Plate(models.Model):
	gel_1008_csv = models.ForeignKey(Gel1008Csv, on_delete=models.CASCADE, null=True, blank=True)
	plate_id = models.CharField(max_length=13, null=True, blank=True)
	holding_rack_id = models.CharField(max_length=11)
	disease_area = models.CharField(max_length=12, choices = (
			("Cancer", "Cancer"),
			("Rare Disease", "Rare Disease"),
			("Unassigned", "Unassigned")), default="Unassigned")
	plate_type = models.CharField(max_length=15, choices=(("Proband", "Proband"),
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
		if self.plate_id:
			return "Plate ID: " + self.plate_id
		else:
			return "Holding Rack ID: " + self.holding_rack_id

class Sample(models.Model):
	rack = models.ForeignKey(Rack, on_delete=models.CASCADE)
	plate = models.ForeignKey(Plate, on_delete=models.CASCADE, null=True, blank=True)
	participant_id = models.CharField(max_length=20)
	group_id = models.CharField(max_length=20)
	priority = models.CharField(max_length=7, choices=(("Routine", "Routine"),
		("Urgent", "Urgent")), default="Routine")
	disease_area = models.CharField(max_length=12, choices = (
			("Cancer", "Cancer"),
			("Rare Disease", "Rare Disease")))
	sample_type = models.CharField(max_length=15, choices=(("Proband", "Proband"),
		("Family", "Family"), ("Cancer Germline", "Cancer Germline"),
		("Tumour", "Tumour"), ("Unassigned", "Unassigned")), default="Unassigned")
	clin_sample_type = models.CharField(max_length=44, choices = sample_types)
	glh_sample_consignment_number = models.CharField(max_length=20)
	laboratory_sample_id = models.CharField(max_length=10, unique=True)
	laboratory_sample_volume = models.IntegerField()
	gmc_rack_well = models.CharField(max_length=3, choices=well_ids)
	is_proband = models.BooleanField()
	is_repeat = models.CharField(max_length=50, choices=(("New", "New"),
		("Retrospective", "Retrospective"), ("Repeat New", "Repeat New"),
		("Repeat Retrospective", "Repeat Retrospective")), default="New")
	tissue_type = models.CharField(max_length=50, choices=(("Normal or Germline sample", "Normal or Germline sample"),
		("Liquid tumour sample", "Liquid tumour sample"), ("Solid tumour sample", "Solid tumour sample"),
		("Abnormal tissue sample", "Abnormal tissue sample"), ("Omics sample", "Omics sample")))
	sample_received = models.BooleanField(default=False)
	sample_matched = models.BooleanField(default=False)
	sample_received_datetime = models.DateTimeField(null=True)
	norm_biorep_sample_vol = models.FloatField(null=True)
	norm_biorep_conc = models.FloatField(null=True)
	plate_well_id = models.CharField(max_length=3, choices=well_ids, null=True)
	issue_identified = models.BooleanField(default=False)
	comment = models.TextField(blank=True, null=True)
	issue_outcome = models.CharField(max_length=64, choices=(("Not resolved", "Not resolved"),
		("Ready for plating", "Ready for plating"),
		("Sample returned to extracting GLH", "Sample returned to extracting GLH"), 
		("Sample destroyed", "Sample destroyed")), blank=True, null=True)

	def __str__(self):
		return self.laboratory_sample_id

class RackScanner(models.Model):
	filename = models.CharField(max_length=60)
	scanned_id = models.CharField(max_length=13)
	date_modified = models.DateTimeField()
	acknowledged = models.BooleanField(default=False)

	class Meta:
		unique_together = (('filename', 'scanned_id', 'date_modified'),)

	def __str__(self):
		return self.filename + ' ' + str(self.date_modified)


class RackScannerSample(models.Model):
	rack_scanner = models.ForeignKey(RackScanner, on_delete=models.CASCADE)
	sample_id = models.CharField(max_length=10)
	position = models.CharField(max_length=3, choices=well_ids)
	matched = models.BooleanField(default=False) 

	class Meta:
		unique_together = (('rack_scanner', 'sample_id', 'position'))

	def __str__(self):
		return self.rack_scanner.scanned_id + ': ' + self.sample_id