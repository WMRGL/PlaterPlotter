from django.db import models

# choice fields
well_ids = (('A1', 'A1'), ('A2', 'A2'), ('A3', 'A3'), ('A4', 'A4'), ('A5', 'A5'), ('A6', 'A6'),
	('A7', 'A7'), ('A8', 'A8'), ('A9', 'A9'), ('A10', 'A10'), ('A11', 'A11'), ('A12', 'A12'),
	('B1', 'B1'), ('B2', 'B2'), ('B3', 'B3'), ('B4', 'B4'), ('B5', 'B5'), ('B6', 'B6'),
	('B7', 'B7'), ('B8', 'B8'), ('B9', 'B9'), ('B10', 'B10'), ('B11', 'B11'), ('B12', 'B12'),
	('C1', 'C1'), ('C2', 'C2'), ('C3', 'C3'), ('C4', 'C4'), ('C5', 'C5'), ('C6', 'C6'),
	('C7', 'C7'), ('C8', 'C8'), ('C9', 'C9'), ('C10', 'C10'), ('C11', 'C11'), ('C12', 'C12'),
	('D1', 'D1'), ('D2', 'D2'), ('D3', 'D3'), ('D4', 'D4'), ('D5', 'D5'), ('D6', 'D6'),
	('D7', 'D7'), ('D8', 'D8'), ('D9', 'D9'), ('D10', 'D10'), ('D11', 'D11'), ('D12', 'D12'),
	('E1', 'E1'), ('E2', 'E2'), ('E3', 'E3'), ('E4', 'E4'), ('E5', 'E5'), ('E6', 'E6'),
	('E7', 'E7'), ('E8', 'E8'), ('E9', 'E9'), ('E10', 'E10'), ('E11', 'E11'), ('E12', 'E12'),
	('F1', 'F1'), ('F2', 'F2'), ('F3', 'F3'), ('F4', 'F4'), ('F5', 'F5'), ('F6', 'F6'),
	('F7', 'F7'), ('F8', 'F8'), ('F9', 'F9'), ('F10', 'F10'), ('F11', 'F11'), ('F12', 'F12'),
	('G1', 'G1'), ('G2', 'G2'), ('G3', 'G3'), ('G4', 'G4'), ('G5', 'G5'), ('G6', 'G6'),
	('G7', 'G7'), ('G8', 'G8'), ('G9', 'G9'), ('G10', 'G10'), ('G11', 'G11'), ('G12', 'G12'),
	('H1', 'H1'), ('H2', 'H2'), ('H3', 'H3'), ('H4', 'H4'), ('H5', 'H5'), ('H6', 'H6'),
	('H7', 'H7'), ('H8', 'H8'), ('H9', 'H9'), ('H10', 'H10'), ('H11', 'H11'), ('H12', 'H12'),)
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

class Gel1004Csv(models.Model):
	gel_1005_csv = models.ForeignKey(Gel1005Csv, on_delete=models.CASCADE, null=True, blank=True)
	filename = models.CharField(max_length=60)
	plating_organisation = models.CharField(max_length=10, choices=lab_ids, default="wwm")
	report_received_datetime = models.DateTimeField()

class Gel1008Csv(models.Model):
	filename = models.CharField(max_length=60)
	report_generated_datetime = models.DateTimeField()
	consignment_number = models.CharField(max_length=10, null=True, blank=True)
	date_of_dispatch = models.DateTimeField(null=True, blank=True)

class Rack(models.Model):
	gel_1004_csv = models.ForeignKey(Gel1004Csv, on_delete=models.CASCADE)
	gmc_rack_id = models.CharField(max_length=11)
	laboratory_id = models.CharField(max_length=3, choices=lab_ids)
	rack_acknowledged = models.BooleanField(default=False)

class Plate(models.Model):
	gel_1008_csv = models.ForeignKey(Gel1008Csv, on_delete=models.CASCADE, null=True, blank=True)
	plate_id = models.CharField(max_length=13, null=True, blank=True)
	holding_rack_id = models.CharField(max_length=11)
	disease_area = models.CharField(max_length=12, choices = (
			("Solid Tumour", "Solid Tumour"),
			("Rare Disease", "Rare Disease"),
			("Unassigned", "Unassigned")), default="Unassigned")
	plate_type = models.CharField(max_length=15, choices=(("Proband", "Proband"),
		("Parent", "Parent"), ("Cancer Germline", "Cancer Germline"),
		("Tumour", "Tumour"), ("Unassigned", "Unassigned")), default="Unassigned")
	priority = models.CharField(max_length=10, choices=(("Routine", "Routine"),
		("Urgent", "Urgent"),
		("Unassigned", "Unassigned")), default="Unassigned")
	half_full = models.BooleanField(default=False)
	full = models.BooleanField(default=False)
	ready_to_plate = models.BooleanField(default=False)

class Sample(models.Model):
	rack = models.ForeignKey(Rack, on_delete=models.CASCADE)
	plate = models.ForeignKey(Plate, on_delete=models.CASCADE, null=True, blank=True)
	participant_id = models.CharField(max_length=20)
	group_id = models.CharField(max_length=20)
	priority = models.CharField(max_length=7, choices=(("Routine", "Routine"),
		("Urgent", "Urgent")), default="Routine")
	disease_area = models.CharField(max_length=12, choices = (
			("Solid Tumour", "Solid Tumour"),
			("Rare Disease", "Rare Disease")))
	sample_type = models.CharField(max_length=15, choices=(("Proband", "Proband"),
		("Parent", "Parent"), ("Cancer Germline", "Cancer Germline"),
		("Tumour", "Tumour"), ("Unassigned", "Unassigned")), default="Unassigned")
	clin_sample_type = models.CharField(max_length=44, choices = sample_types)
	glh_sample_consignment_number = models.CharField(max_length=20)
	laboratory_sample_id = models.CharField(max_length=10)
	laboratory_sample_volume = models.IntegerField()
	gmc_rack_well = models.CharField(max_length=3, choices=well_ids)
	is_proband = models.BooleanField()
	sample_received = models.BooleanField(default=False)
	sample_received_datetime = models.DateTimeField(null=True)
	norm_biorep_sample_vol = models.FloatField(null=True)
	norm_biorep_conc = models.FloatField(null=True)
	plate_well_id = models.CharField(max_length=3, choices=well_ids, null=True)