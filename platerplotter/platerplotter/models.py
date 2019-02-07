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



