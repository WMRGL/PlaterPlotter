from django.db import models

# Create your models here.
class Gel1004csv(models.Model):
	filename = models.CharField(max_length=60)
	participantId = models.CharField(max_length=20)
	groupId = models.CharField(max_length=20)
	diseaseArea = models.CharField(max_length=12, choices = (
			("Solid Tumour", "Solid Tumour"),
			("Rare Disease", "Rare Disease")))
	gmcRackId = models.CharField(max_length=11)
	clinSampleType = models.CharField(max_length=44, choices = (
		("dna_blood_germline", "dna_blood_germline"),
		("dna_saliva", "dna_saliva"),
		("dna_fibroblast", "dna_fibroblast"),
		("dna_ff_germline", "dna_ff_germline"),
		("dna_ffpe_tumour", "dna_ffpe_tumour"),
		("dna_ff_tumour", "dna_ff_tumour"),
		("dna_blood_tumour", "dna_blood_tumour"),
		("dna_bone_marrow_aspirate_tumour_sorted_cells", "dna_bone_marrow_aspirate_tumour_sorted_cells"),
		("dna_bone_marrow_aspirate_tumour_cells", "dna_bone_marrow_aspirate_tumour_cells"),
		("tumour_tissue_ffpe", "tumour_tissue_ffpe"),
		("lysate_ffpe", "lysate_ffpe"),
		("lysate_ff", "lysate_ff"),
		("lysed_tumour_cells", "lysed_tumour_cells"),
		("buffy_coat", "buffy_coat"),
		("streck_plasma", "streck_plasma"),
		("edta_plasma", "edta_plasma"),
		("lihep_plasma", "lihep_plasma"),
		("serum", "serum"),
		("rna_blood", "rna_blood"),
		("tumour_tissue_ff", "tumour_tissue_ff"),
		("bone_marrow_rna_gtc", "bone_marrow_rna_gtc"),
		("blood_rna_gtc", "blood_rna_gtc"),
		("dna_amniotic_fluid", "dna_amniotic_fluid"),
		("dna_fresh_amniotic_fluid", "dna_fresh_amniotic_fluid"),
		("dna_sorted_cd138_positive_cells", "dna_sorted_cd138_positive_cells"),
		("dna_edta_blood", "dna_edta_blood"),
		("dna_li_hep_blood", "dna_li_hep_blood"),
		("dna_bone_marrow", "dna_bone_marrow"),
		("dna_chorionic_villus_sample", "dna_chorionic_villus_sample"),
		("dna_fresh_chronic_villus_sample", "dna_fresh_chronic_villus_sample"),
		("dna_unknown", "dna_unknown"),
		("dna_unkown_tumour", "dna_unkown_tumour"),
		("dna_fetal_edta_blood", "dna_fetal_edta_blood"),
		("dna_fibroblast_culture", "dna_fibroblast_culture"),
		("dna_fresh_fluid_sorted_other", "dna_fresh_fluid_sorted_other"),
		("dna_fresh_fluid_unsorted", "dna_fresh_fluid_unsorted"),
		("dna_other", "dna_other"),
		("dna_fresh_frozen_tissue", "dna_fresh_frozen_tissue"),
		("dna_fresh_tissue_in_culture_medium", "dna_fresh_tissue_in_culture_medium"),
		("dna_fresh_fluid_tumour", "dna_fresh_fluid_tumour"),
		("dna_fresh_frozen_tumour", "dna_fresh_frozen_tumour")))
	glhSampleConsignmentNumber = models.CharField(max_length=20)
	laboratorySampleId = models.CharField(max_length=10)
	laboratoryId = models.CharField(max_length=3, choices= (("yne", "yne"), ("now", "now"), 
		("eme", "eme"), ("lnn", "lnn"), ("lns", "lns"), ("wwm", "wwm"), ("sow", "sow")))
	laboratorySampleVolume = models.IntegerField()
	gmcRackWell = models.CharField(max_length=3)
	platingOrganisation = models.CharField(max_length=10, default="wwm")
	priority = models.CharField(max_length=7, choices=(("Routine", "Routine"),
		("Urgent", "Urgent")), default="Routine")
	isProband = models.BooleanField()

class ReveivedSamples(models.Model):
	gmcRackId = models.CharField(max_length=11)
	sampleReceivedDateTime = models.DateTimeField()
	A1 = models.CharField(max_length=10, blank=True)
	A2 = models.CharField(max_length=10, blank=True)
	A3 = models.CharField(max_length=10, blank=True)
	A4 = models.CharField(max_length=10, blank=True)
	A5 = models.CharField(max_length=10, blank=True)
	A6 = models.CharField(max_length=10, blank=True)
	A7 = models.CharField(max_length=10, blank=True)
	A8 = models.CharField(max_length=10, blank=True)
	A9 = models.CharField(max_length=10, blank=True)
	A10 = models.CharField(max_length=10, blank=True)
	A11 = models.CharField(max_length=10, blank=True)
	A12 = models.CharField(max_length=10, blank=True)
	B1 = models.CharField(max_length=10, blank=True)
	B2 = models.CharField(max_length=10, blank=True)
	B3 = models.CharField(max_length=10, blank=True)
	B4 = models.CharField(max_length=10, blank=True)
	B5 = models.CharField(max_length=10, blank=True)
	B6 = models.CharField(max_length=10, blank=True)
	B7 = models.CharField(max_length=10, blank=True)
	B8 = models.CharField(max_length=10, blank=True)
	B9 = models.CharField(max_length=10, blank=True)
	B10 = models.CharField(max_length=10, blank=True)
	B11 = models.CharField(max_length=10, blank=True)
	B12 = models.CharField(max_length=10, blank=True)
	C1 = models.CharField(max_length=10, blank=True)
	C2 = models.CharField(max_length=10, blank=True)
	C3 = models.CharField(max_length=10, blank=True)
	C4 = models.CharField(max_length=10, blank=True)
	C5 = models.CharField(max_length=10, blank=True)
	C6 = models.CharField(max_length=10, blank=True)
	C7 = models.CharField(max_length=10, blank=True)
	C8 = models.CharField(max_length=10, blank=True)
	C9 = models.CharField(max_length=10, blank=True)
	C10 = models.CharField(max_length=10, blank=True)
	C11 = models.CharField(max_length=10, blank=True)
	C12 = models.CharField(max_length=10, blank=True)
	D1 = models.CharField(max_length=10, blank=True)
	D2 = models.CharField(max_length=10, blank=True)
	D3 = models.CharField(max_length=10, blank=True)
	D4 = models.CharField(max_length=10, blank=True)
	D5 = models.CharField(max_length=10, blank=True)
	D6 = models.CharField(max_length=10, blank=True)
	D7 = models.CharField(max_length=10, blank=True)
	D8 = models.CharField(max_length=10, blank=True)
	D9 = models.CharField(max_length=10, blank=True)
	D10 = models.CharField(max_length=10, blank=True)
	D11 = models.CharField(max_length=10, blank=True)
	D12 = models.CharField(max_length=10, blank=True)
	E1 = models.CharField(max_length=10, blank=True)
	E2 = models.CharField(max_length=10, blank=True)
	E3 = models.CharField(max_length=10, blank=True)
	E4 = models.CharField(max_length=10, blank=True)
	E5 = models.CharField(max_length=10, blank=True)
	E6 = models.CharField(max_length=10, blank=True)
	E7 = models.CharField(max_length=10, blank=True)
	E8 = models.CharField(max_length=10, blank=True)
	E9 = models.CharField(max_length=10, blank=True)
	E10 = models.CharField(max_length=10, blank=True)
	E11 = models.CharField(max_length=10, blank=True)
	E12 = models.CharField(max_length=10, blank=True)
	F1 = models.CharField(max_length=10, blank=True)
	F2 = models.CharField(max_length=10, blank=True)
	F3 = models.CharField(max_length=10, blank=True)
	F4 = models.CharField(max_length=10, blank=True)
	F5 = models.CharField(max_length=10, blank=True)
	F6 = models.CharField(max_length=10, blank=True)
	F7 = models.CharField(max_length=10, blank=True)
	F8 = models.CharField(max_length=10, blank=True)
	F9 = models.CharField(max_length=10, blank=True)
	F10 = models.CharField(max_length=10, blank=True)
	F11 = models.CharField(max_length=10, blank=True)
	F12 = models.CharField(max_length=10, blank=True)
	G1 = models.CharField(max_length=10, blank=True)
	G2 = models.CharField(max_length=10, blank=True)
	G3 = models.CharField(max_length=10, blank=True)
	G4 = models.CharField(max_length=10, blank=True)
	G5 = models.CharField(max_length=10, blank=True)
	G6 = models.CharField(max_length=10, blank=True)
	G7 = models.CharField(max_length=10, blank=True)
	G8 = models.CharField(max_length=10, blank=True)
	G9 = models.CharField(max_length=10, blank=True)
	G10 = models.CharField(max_length=10, blank=True)
	G11 = models.CharField(max_length=10, blank=True)
	G12 = models.CharField(max_length=10, blank=True)
	H1 = models.CharField(max_length=10, blank=True)
	H2 = models.CharField(max_length=10, blank=True)
	H3 = models.CharField(max_length=10, blank=True)
	H4 = models.CharField(max_length=10, blank=True)
	H5 = models.CharField(max_length=10, blank=True)
	H6 = models.CharField(max_length=10, blank=True)
	H7 = models.CharField(max_length=10, blank=True)
	H8 = models.CharField(max_length=10, blank=True)
	H9 = models.CharField(max_length=10, blank=True)
	H10 = models.CharField(max_length=10, blank=True)
	H11 = models.CharField(max_length=10, blank=True)
	H12 = models.CharField(max_length=10, blank=True)

class Gel1005csv(models.Model):
	filename = models.CharField(max_length=60)
	participantId = models.CharField(max_length=20)
	laboratoryId = models.CharField(max_length=3, choices= (("yne", "yne"), ("now", "now"), 
		("eme", "eme"), ("lnn", "lnn"), ("lns", "lns"), ("wwm", "wwm"), ("sow", "sow")))
	sampleReceived = models.BooleanField()
	sampleReceivedDateTime = models.DateTimeField()
	reportGeneratedDateTime = models.DateTimeField()
	laboratorySampleId = models.CharField(max_length=10)

