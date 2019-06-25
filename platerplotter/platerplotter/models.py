from django.db import models

# choice fields
well_ids = (('A01', 'A01'), ('A02', 'A02'), ('A03', 'A03'), ('A04', 'A04'), ('A05', 'A05'), ('A06', 'A06'),
	('A07', 'A07'), ('A08', 'A08'), ('A09', 'A09'), ('A10', 'A10'), ('A11', 'A11'), ('A12', 'A12'),
	('B01', 'B01'), ('B02', 'B02'), ('B03', 'B03'), ('B04', 'B04'), ('B05', 'B05'), ('B06', 'B06'),
	('B07', 'B07'), ('B08', 'B08'), ('B09', 'B09'), ('B10', 'B10'), ('B11', 'B11'), ('B12', 'B12'),
	('C01', 'C01'), ('C02', 'C02'), ('C03', 'C03'), ('C04', 'C04'), ('C05', 'C05'), ('C06', 'C06'),
	('C07', 'C07'), ('C08', 'C08'), ('C09', 'C09'), ('C10', 'C10'), ('C11', 'C11'), ('C12', 'C12'),
	('D01', 'D01'), ('D02', 'D02'), ('D03', 'D03'), ('D04', 'D04'), ('D05', 'D05'), ('D06', 'D06'),
	('D07', 'D07'), ('D08', 'D08'), ('D09', 'D09'), ('D10', 'D10'), ('D11', 'D11'), ('D12', 'D12'),
	('E01', 'E01'), ('E02', 'E02'), ('E03', 'E03'), ('E04', 'E04'), ('E05', 'E05'), ('E06', 'E06'),
	('E07', 'E07'), ('E08', 'E08'), ('E09', 'E09'), ('E10', 'E10'), ('E11', 'E11'), ('E12', 'E12'),
	('F01', 'F01'), ('F02', 'F02'), ('F03', 'F03'), ('F04', 'F04'), ('F05', 'F05'), ('F06', 'F06'),
	('F07', 'F07'), ('F08', 'F08'), ('F09', 'F09'), ('F10', 'F10'), ('F11', 'F11'), ('F12', 'F12'),
	('G01', 'G01'), ('G02', 'G02'), ('G03', 'G03'), ('G04', 'G04'), ('G05', 'G05'), ('G06', 'G06'),
	('G07', 'G07'), ('G08', 'G08'), ('G09', 'G09'), ('G10', 'G10'), ('G11', 'G11'), ('G12', 'G12'),
	('H01', 'H01'), ('H02', 'H02'), ('H03', 'H03'), ('H04', 'H04'), ('H05', 'H05'), ('H06', 'H06'),
	('H07', 'H07'), ('H08', 'H08'), ('H09', 'H09'), ('H10', 'H10'), ('H11', 'H11'), ('H12', 'H12'),)
lab_ids = (("yne", "yne"), ("now", "now"), ("eme", "eme"), ("lnn", "lnn"), ("lns", "lns"), 
	("wwm", "wwm"), ("sow", "sow"))
sample_types = (("dna_blood_germline", "dna_blood_germline"), ("dna_saliva", "dna_saliva"),
	("dna_fibroblast", "dna_fibroblast"), ("dna_ff_germline", "dna_ff_germline"),
	("dna_ffpe_tumour", "dna_ffpe_tumour"), ("dna_ff_tumour", "dna_ff_tumour"),
	("dna_blood_tumour", "dna_blood_tumour"),
	("dna_bone_marrow_aspirate_tumour_sorted_cells", "dna_bone_marrow_aspirate_tumour_sorted_cells"),
	("dna_bone_marrow_aspirate_tumour_cells", "dna_bone_marrow_aspirate_tumour_cells"),
	("tumour_tissue_ffpe", "tumour_tissue_ffpe"), ("lysate_ffpe", "lysate_ffpe"),
	("lysate_ff", "lysate_ff"), ("lysed_tumour_cells", "lysed_tumour_cells"), 
	("buffy_coat", "buffy_coat"), ("streck_plasma", "streck_plasma"), ("edta_plasma", "edta_plasma"),
	("lihep_plasma", "lihep_plasma"), ("serum", "serum"), ("rna_blood", "rna_blood"),
	("tumour_tissue_ff", "tumour_tissue_ff"), ("bone_marrow_rna_gtc", "bone_marrow_rna_gtc"),
	("blood_rna_gtc", "blood_rna_gtc"), ("dna_amniotic_fluid", "dna_amniotic_fluid"),
	("dna_fresh_amniotic_fluid", "dna_fresh_amniotic_fluid"),
	("dna_sorted_cd138_positive_cells", "dna_sorted_cd138_positive_cells"),
	("dna_edta_blood", "dna_edta_blood"), ("dna_li_hep_blood", "dna_li_hep_blood"),
	("dna_bone_marrow", "dna_bone_marrow"), ("dna_chorionic_villus_sample", "dna_chorionic_villus_sample"),
	("dna_fresh_chronic_villus_sample", "dna_fresh_chronic_villus_sample"), ("dna_unknown", "dna_unknown"),
	("dna_unkown_tumour", "dna_unkown_tumour"), ("dna_fetal_edta_blood", "dna_fetal_edta_blood"),
	("dna_fibroblast_culture", "dna_fibroblast_culture"), 
	("dna_fresh_fluid_sorted_other", "dna_fresh_fluid_sorted_other"), 
	("dna_fresh_fluid_unsorted", "dna_fresh_fluid_unsorted"), ("dna_other", "dna_other"),
	("dna_fresh_frozen_tissue", "dna_fresh_frozen_tissue"), 
	("dna_fresh_tissue_in_culture_medium", "dna_fresh_tissue_in_culture_medium"),
	("dna_fresh_fluid_tumour", "dna_fresh_fluid_tumour"), 
	("dna_fresh_frozen_tumour", "dna_fresh_frozen_tumour"))

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
	gmc_rack_id = models.CharField(max_length=11)
	laboratory_id = models.CharField(max_length=3, choices=lab_ids)
	rack_acknowledged = models.BooleanField(default=False)

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
		("Tumour", "Tumour"), ("Unassigned", "Unassigned")), default="Unassigned")
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