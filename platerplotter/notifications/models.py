from django.db import models

# Create your models here.

lab_ids = (
	("yne", "yne"), ("now", "now"), ("eme", "eme"), ("lnn", "lnn"), ("lns", "lns"), ("wwm", "wwm"), ("sow", "sow")
)


class Gel1005Csv(models.Model):
	filename = models.CharField(max_length=60)
	report_generated_datetime = models.DateTimeField()

	def __str__(self):
		return self.filename

	class Meta:
		app_label = 'platerplotter'
		db_table = 'Gel1005Csv'
		verbose_name = 'Gel1005 CSV'
		verbose_name_plural = 'Gel1005 CSVs'


class Gel1004Csv(models.Model):
	gel_1005_csv = models.ForeignKey(Gel1005Csv, on_delete=models.CASCADE, null=True, blank=True)
	filename = models.CharField(max_length=60)
	plating_organisation = models.CharField(max_length=10, choices=lab_ids, default="wwm")
	report_received_datetime = models.DateTimeField()

	def __str__(self):
		return self.filename

	class Meta:
		app_label = 'platerplotter'
		db_table = 'Gel1004Csv'
		verbose_name = 'Gel1004 CSV'
		verbose_name_plural = 'Gel1004 CSVs'


class ReceivingRack(models.Model):
	gel_1004_csv = models.ForeignKey(Gel1004Csv, on_delete=models.CASCADE)
	receiving_rack_id = models.CharField(max_length=12)
	laboratory_id = models.CharField(max_length=3, choices=lab_ids)
	glh_sample_consignment_number = models.CharField(max_length=50)
	rack_acknowledged = models.BooleanField(default=False)
	volume_checked = models.BooleanField(default=False)
	disease_area = models.CharField(max_length=12, choices=(
		("Cancer", "Cancer"),
		("Rare Disease", "Rare Disease"),
		("Mixed", "Mixed")), null=True, blank=True)
	rack_type = models.CharField(max_length=15, choices=(
		("Proband", "Proband"), ("Family", "Family"), ("Cancer Germline", "Cancer Germline"), ("Tumour", "Tumour"),
		("Mixed", "Mixed")), null=True, blank=True)
	priority = models.CharField(max_length=10, choices=(
		("Routine", "Routine"), ("Urgent", "Urgent"), ("Mixed", "Mixed")), null=True, blank=True)


	def __str__(self):
		return self.receiving_rack_id

	def is_empty(self):
		samples = Sample.objects.filter(receiving_rack=self)
		empty = True
		for sample in samples:
			if not hasattr(sample, 'holding_rack_well'):
				empty = False
		return empty

	class Meta:
		app_label = 'platerplotter'
		db_table = 'ReceivingRack'
		verbose_name = 'Receiving rack'
		verbose_name_plural = 'Receiving racks'
