from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.urls import reverse
from platerplotter.models import Gel1004Csv, Gel1005Csv, Gel1008Csv, Rack, Plate, Sample, RackScanner, RackScannerSample
from platerplotter.config.load_config import LoadConfig
from platerplotter.forms import HoldingRackForm, SampleSelectForm, PlatingForm, Gel1008Form
from datetime import datetime
from django.core.exceptions import ValidationError
from platerplotter.plate_manager import PlateManager
import csv
import os
import pytz
import re


# def ajax_change_sample_received_status(request):
#     sample_received = request.GET.get('sample_received', False)
#     sample_id = request.GET.get('sample_id', False)
#     # first you get your Job model
#     sample = Sample.objects.get(pk=sample_id)
#     try:
#         sample.sample_received = sample_received
#         sample.save()
#         return JsonResponse({"success": True})
#     except Exception as e:
#         return JsonResponse({"success": False})
#     return JsonResponse(data)

# def remove_padded_zeros(position):
# 	letter = position[0]
# 	number = position[1:]
# 	if number[0] == '0':
# 		number = number[1]
# 	return letter + number

def pad_zeros(well):
	if len(well) == 2:
		return well[0] + '0' + well[1]
	else: 
		return well

def check_plating_organisation(plating_organisation):
	if plating_organisation != 'wwm':
		raise ValueError('Plating orgnaisation entered as {}. Expected "wmm".'.format(plating_organisation.lower()))
	else:
		return plating_organisation.lower()

def check_rack_id(rack_id):
	if not re.match(r'^[a-zA-Z]{2}\d{8}$', rack_id):
		raise ValueError('Incorrect rack ID. Received {} which does not match the required specification.'.format(rack_id))
	else:
		return rack_id.upper()

def check_laboratory_id(laboratory_id):
	accepted_ids = ["yne", "now", "eme", "lnn", "lns", "wwm", "sow"]
	if laboratory_id not in accepted_ids:
		raise ValueError('Incorrect laboratory ID. Received {} which is not on the list of accepted laboratory IDs.'.format(laboratory_id))
	else:
		return laboratory_id

def check_participant_id(participant_id):
	if not re.match(r'^[p,P]\d{11}$', participant_id):
		raise ValueError('Incorrect participant ID. Received {} which does not match the required specification.'.format(participant_id))
	else:
		return participant_id

def check_group_id(group_id):
	if not re.match(r'^[r,R]\d{11}$', group_id):
		raise ValueError('Incorrect group ID. Received {} which does not match the required specification.'.format(group_id))
	else:
		return group_id

def check_priority(priority):
	accepted_values = ['URGENT', 'ROUTINE']
	if priority.upper() not in accepted_values:
		raise ValueError('Incorrect priority. Received {}. Must be either routine or urgent.'.format(priority))
	else:
		return priority

def check_disease_area(disease_area):
	accepted_values = ['CANCER', 'RARE DISEASE']
	if disease_area.upper() not in accepted_values:
		raise ValueError('Incorrect disease area. Received {}. Must be either cancer or rare disease.'.format(priority))
	else:
		return disease_area

def check_clinical_sample_type(clin_sample_type):
	accepted_values = ["dna_blood_germline","dna_saliva","dna_fibroblast","dna_ff_germline",
		"dna_ffpe_tumour","dna_ff_tumour","dna_blood_tumour","dna_bone_marrow_aspirate_tumour_sorted_cells",
		"dna_bone_marrow_aspirate_tumour_cells","tumour_tissue_ffpe","lysate_ffpe","lysate_ff",
		"lysed_tumour_cells","buffy_coat","streck_plasma","edta_plasma","lihep_plasma","serum",
		"rna_blood","tumour_tissue_ff","bone_marrow_rna_gtc","blood_rna_gtc","dna_amniotic_fluid",
		"dna_fresh_amniotic_fluid","dna_sorted_cd138_positive_cells","dna_edta_blood","dna_li_hep_blood",
		"dna_bone_marrow","dna_chorionic_villus_sample","dna_fresh_chronic_villus_sample","dna_unknown",
		"dna_unkown_tumour","dna_fetal_edta_blood","dna_fibroblast_culture","dna_fresh_fluid_sorted_other",
		"dna_fresh_fluid_unsorted","dna_other","dna_fresh_frozen_tissue","dna_fresh_tissue_in_culture_medium",
		"dna_fresh_fluid_tumour","dna_fresh_frozen_tumour"]
	if clin_sample_type.lower() not in accepted_values:
		raise ValueError('Clinical sample type not in list of accepted values. Received {}.'.format(clin_sample_type))
	else:
		return clin_sample_type.lower()

def check_glh_sample_consignment_number(glh_sample_consignment_number):
	if not re.match(r'^[a-z,A-Z]{3}-\d{4}-\d{2}-\d{2}-\d{2}-[1,2]$', glh_sample_consignment_number):
		raise ValueError('Incorrect GLH sample consignment number. Received {} which does not match the required specification.'.format(glh_sample_consignment_number))
	else:
		return glh_sample_consignment_number

def check_laboratory_sample_id(laboratory_sample_id):
	if not re.match(r'^\d{10}$', laboratory_sample_id):
		raise ValueError('Incorrect laboratory sample ID. Received {}. Should be 10 digits'.format(laboratory_sample_id))
	else:
		return laboratory_sample_id

def check_laboratory_sample_volume(laboratory_sample_volume):
	if not re.match(r'^\d*$', laboratory_sample_volume):
		raise ValueError('Incorrect laboratory sample volume. Received {}. Should be all digits'.format(laboratory_sample_volume))
	else:
		return laboratory_sample_volume

def check_rack_well(rack_well):
	if not re.match(r'^[A-H][0,1][0-9]$', rack_well):
		raise ValueError('Invalid rack well for a 96 well rack. Received {}.'.format(rack_well))
	else:
		return rack_well

def check_is_proband(is_proband):
	if is_proband == "TRUE":
		return True
	if is_proband == "FALSE":
		return False
	if type(is_proband) == type(True):
		return is_proband
	else:
		raise ValueError('Invalid value for Is Proband. Received {} but expected a boolean value'.format(is_proband))

def check_is_repeat(is_repeat):
	accepted_values = ['New', 'Retrospective', 'Repeat New', 'Repeat Retrospective']
	if is_repeat not in accepted_values:
		raise ValueError('Is repeat field not in list of accepted values. Received {}.'.format(is_repeat))
	else:
		return is_repeat

def check_tissue_type(tissue_type):
	accepted_values = ["Normal or Germline sample", "Liquid tumour sample", "Solid tumour sample", "Abnormal tissue sample", "Omics sample"]
	if tissue_type not in accepted_values:
		raise ValueError('Tissue type not in list of accepted values. Received {}.'.format(tissue_type))
	else:
		return tissue_type

def rack_scan():
	directory = LoadConfig().load()['rack_scanner_path']
	for filename in os.listdir(directory):
		if filename.endswith(".csv"):
			path = directory + filename
			date_modified = datetime.fromtimestamp(os.path.getmtime(path), pytz.timezone('UTC'))
			with open(path, 'r') as csvFile:
				reader = csv.reader(csvFile, delimiter=',', skipinitialspace=True)
				for row in reader:
					if row[1] != 'NO READ':
						rack_scanner, created = RackScanner.objects.get_or_create(
							filename=filename,
							scanned_id=row[3].strip(),
							date_modified=date_modified)
						RackScannerSample.objects.get_or_create(rack_scanner=rack_scanner,
							sample_id=row[1].strip(),
							position=pad_zeros(row[0].strip()))
			os.rename(path, directory + "processed/" + filename)

def import_acks(request):
	"""
	Renders import acks page. Allows users to import new GEL1004 acks
	and acknowledge receipt of samples.
	"""
	if request.method == 'POST':
		# import new notifications from the storage location
		if 'import-1004' in request.POST:
			directory = LoadConfig().load()['gel1004path']
			for filename in os.listdir(directory):
				if filename.endswith(".csv"):
					datetime_now = datetime.now(pytz.timezone('UTC'))
					path = directory + filename
					with open(path) as csv_file:
						csv_reader = csv.reader(csv_file, delimiter=',')
						line_count=0
						for row in csv_reader:
							if line_count == 0:
								line_count += 1
							else:
								# gets exiting, or creates new objects
								try:
									gel_1004_csv = Gel1004Csv.objects.get(
										filename = filename,
										plating_organisation=check_plating_organisation(row[10].strip()))
								except:
									gel_1004_csv = Gel1004Csv.objects.create(
										filename = filename,
										plating_organisation=check_plating_organisation(row[10].strip()),
										report_received_datetime = datetime_now)
								try:
									rack = Rack.objects.get(
										gel_1004_csv = gel_1004_csv,
										gmc_rack_id = check_rack_id(row[3].strip()),
										laboratory_id = check_laboratory_id(row[7].strip()))
								except:
									rack = Rack.objects.create(
										gel_1004_csv = gel_1004_csv,
										gmc_rack_id = check_rack_id(row[3].strip()),
										laboratory_id = check_laboratory_id(row[7].strip()))
								# creates new Sample object
								# need to add regex error checking to input
								sample = Sample.objects.create(
									rack = rack,
									participant_id = check_participant_id(row[0].strip()),
									group_id = check_group_id(row[1].strip()),
									priority = check_priority(row[11].strip()),
									disease_area = check_disease_area(row[2].strip()),
									clin_sample_type = check_clinical_sample_type(row[4].strip()),
									glh_sample_consignment_number = check_glh_sample_consignment_number(row[5].strip()),
									laboratory_sample_id = check_laboratory_sample_id(row[6].strip()),
									laboratory_sample_volume = check_laboratory_sample_volume(row[8].strip()),
									gmc_rack_well = check_rack_well(row[9].strip()),
									is_proband=check_is_proband(row[12].strip()),
									is_repeat = check_is_repeat(row[13].strip()),
									tissue_type=check_tissue_type(row[14].strip()))
								sample = Sample.objects.get(pk=sample.pk)
								if sample.disease_area == 'Rare Disease':
									if sample.is_proband:
										sample.sample_type = 'Proband'
									else:
										sample.sample_type = 'Family'
								elif sample.disease_area == 'Cancer':
									if 'tumour' in sample.tissue_type:
										sample.sample_type = 'Tumour'
									else:
										sample.sample_type = 'Cancer Germline'
								sample.save()
								line_count += 1
					os.rename(path, directory + "processed/" + filename)
			return HttpResponseRedirect('/')
		# Generate GEL1005 acks for received samples
		if 	'send-1005' in request.POST:
			pk = request.POST['send-1005']
			gel_1004 = Gel1004Csv.objects.get(pk=pk)
			racks = Rack.objects.filter(gel_1004_csv=gel_1004)
			directory = LoadConfig().load()['gel1005path']
			datetime_now = datetime.now(pytz.timezone('UTC'))
			filename = "ngis_bio_to_gel_samples_received_" + datetime.now(pytz.timezone('UTC')).strftime("%y%m%d_%H%M%S") + ".csv"
			gel_1005 = Gel1005Csv.objects.create(
				filename=filename,
				report_generated_datetime=datetime_now)
			gel_1004.gel_1005_csv = gel_1005
			gel_1004.save()
			path = directory + filename
			with open(path, 'w', newline='') as csvfile:
				writer = csv.writer(csvfile, delimiter=',',
					quotechar=',', quoting=csv.QUOTE_MINIMAL)
				writer.writerow(['Participant ID', 'Laboratory ID',
					'Sample Received', 'Sample Received DateTime',
					'DateTime Report Generated', 'Laboratory Sample ID'])
				for rack in racks:
					samples = Sample.objects.filter(rack=rack)
					for sample in samples:
						received_datetime = ''
						if sample.sample_received_datetime:
							received_datetime = sample.sample_received_datetime.replace(microsecond=0).isoformat().replace('+00:00', 'Z')
						writer.writerow([sample.participant_id, rack.laboratory_id,
							sample.sample_received, received_datetime,
							gel_1005.report_generated_datetime.replace(microsecond=0).isoformat().replace('+00:00', 'Z'), sample.laboratory_sample_id])
			return HttpResponseRedirect('/')
	unacked_gel_1004 = Gel1004Csv.objects.filter(gel_1005_csv__isnull = True)
	unacked_racks_dict = {}
	for gel_1004 in unacked_gel_1004:
		unacked_racks_dict[gel_1004] = Rack.objects.filter(gel_1004_csv=gel_1004)
		for gel_1004, racks in unacked_racks_dict.items():
			all_racks_acked = True
			for rack in racks:
				rack.no_samples = Sample.objects.filter(rack=rack).count()
				if not rack.rack_acknowledged:
					all_racks_acked = False
			gel_1004.all_racks_acked = all_racks_acked
	return render(request, 'import-acks.html', {"unacked_racks_dict" : unacked_racks_dict})

def acknowledge_samples(request, gel1004, rack):
	rack = Rack.objects.get(gel_1004_csv=gel1004, gmc_rack_id=rack)
	samples = Sample.objects.filter(rack=rack)
	sample_select_form = SampleSelectForm()
	if request.method == 'POST':
		if 'rack-scanner' in request.POST:
			rack_scan()
			rack_scanner = RackScanner.objects.filter(scanned_id=rack.gmc_rack_id,
				acknowledged=False).order_by('-date_modified')
			if rack_scanner:
				rack_scanner_samples = RackScannerSample.objects.filter(rack_scanner=rack_scanner[0])
				samples_received_wrong_position = []
				extra_samples = []
				for sample in samples:
					for rack_scanner_sample in rack_scanner_samples:
						if sample.laboratory_sample_id == rack_scanner_sample.sample_id:
							if sample.gmc_rack_well == rack_scanner_sample.position:
								sample.sample_received = True
								sample.sample_received_datetime = datetime.now(pytz.timezone('UTC'))
								sample.save()
								rack_scanner_sample.matched = True
								rack_scanner_sample.save()
							else:
								samples_received_wrong_position.append(sample)
				for rack_scanner_sample in rack_scanner_samples:
					if not rack_scanner_sample.matched:
						extra_samples.append(rack_scanner_sample)
				if samples_received_wrong_position or extra_samples:
					messages.error(request, "Rack contains extra samples not listed in the GEL1004 or samples were in the wrong positions")
			else:
				messages.error(request, "Rack " + rack.gmc_rack_id + " not found in Plate/Rack scanner CSV. Has the rack been scanned?")
		if 'rack-acked' in request.POST:
			rack.rack_acknowledged = True
			rack.save()
			return HttpResponseRedirect('/')
		if 'sample-scanned' in request.POST:
			sample_select_form = SampleSelectForm(request.POST)
			if sample_select_form.is_valid():
				lab_sample_id = sample_select_form.cleaned_data.get('lab_sample_id')
				sample = None
				try:
					sample = Sample.objects.get(rack=rack, laboratory_sample_id=lab_sample_id)
				except:
					messages.error(request, "Sample " + lab_sample_id + " does not exist")
				if sample:
					sample.sample_received = True
					sample.sample_received_datetime = datetime.now(pytz.timezone('UTC'))
					sample.save()
			sample_select_form = SampleSelectForm()
		if 'sample-received' in request.POST:
			pk = request.POST['sample-received']
			sample = Sample.objects.get(pk=pk)
			if sample.sample_received:
				sample.sample_received = False
				sample.sample_received_datetime = None
			else:
				sample.sample_received = True
				sample.sample_received_datetime = datetime.now(pytz.timezone('UTC'))
			sample.save()
			url = reverse('acknowledge_samples', kwargs={
				"gel1004" : gel1004,
				"rack" : rack.gmc_rack_id,
				})
			return HttpResponseRedirect(url)
	all_samples_received = True
	for sample in samples:
		if not sample.sample_received:
			all_samples_received = False
	if all_samples_received:
		messages.info(request, "All samples received")
	return render(request, 'acknowledge-samples.html', {"rack" : rack,
		"samples" : samples,
		"sample_select_form" : sample_select_form,
		"all_samples_received" : all_samples_received})

def awaiting_plating(request):
	unplated_samples = Sample.objects.filter(plate__isnull = True, 
		rack__gel_1004_csv__gel_1005_csv__isnull = False,
		sample_received = True)
	unplated_racks_dict = {}
	for sample in unplated_samples:
		if sample.rack in unplated_racks_dict:
			unplated_racks_dict[sample.rack].append(sample)
		else:
			unplated_racks_dict[sample.rack] = [sample] 
	return render(request, 'awaiting-plating.html', {
		"unplated_racks_dict" : unplated_racks_dict})

def plate_samples(request, gel1004, rack, plate_id=None):
	plate_rows = ['A','B','C','D','E','F','G','H']
	plate_columns = ['01','02','03','04','05','06','07','08','09','10','11','12']
	rack = Rack.objects.get(gel_1004_csv=gel1004, gmc_rack_id=rack)
	samples = Sample.objects.filter(rack=rack,
		plate__isnull = True,
		rack__gel_1004_csv__gel_1005_csv__isnull = False,
		sample_received = True)
	samples = sorted(samples, key=lambda x: (x.gmc_rack_well[0], int(x.gmc_rack_well[1:])))
	current_holding_racks = Plate.objects.filter(plate_id__isnull=True)
	current_holding_racks_dict = {}
	for current_holding_rack in current_holding_racks:
		current_holding_racks_dict[current_holding_rack] = Sample.objects.filter(plate=current_holding_rack).count()
	assigned_well_list = []
	if plate_id:
		plate = Plate.objects.get(holding_rack_id=plate_id, plate_id__isnull=True)
		plate_samples = sorted(Sample.objects.filter(plate=plate), 
			key=lambda x: (x.plate_well_id[0], int(x.plate_well_id[1:])), 
			reverse=True)
		plate_manager = PlateManager(plate)
		for sample in plate_samples:
			assigned_well_list.append(sample.plate_well_id)
	else:
		plate = None
		plate_samples = None
	if request.method == 'POST':
		if 'holding' in request.POST:
			sample_select_form = SampleSelectForm()
			holding_rack_form = HoldingRackForm(request.POST)
			if holding_rack_form.is_valid():
				holding_rack_id = holding_rack_form.cleaned_data.get('holding_rack_id')
				if holding_rack_id == rack.gmc_rack_id:
					messages.error(request, "You have scanned the GMC Rack. Please scan the holding rack.")
				else:
					try:
						plate = Plate.objects.get(holding_rack_id=holding_rack_id, plate_id__isnull=True)
					except:
						plate = Plate.objects.create(holding_rack_id=holding_rack_id)
				if plate:
					url = reverse('plate_samples', kwargs={
							'gel1004' : rack.gel_1004_csv.pk,
							'rack' : rack.gmc_rack_id,
							'plate_id' : plate.holding_rack_id,
							})
				else:
					url = reverse('plate_samples', kwargs={
							'gel1004' : rack.gel_1004_csv.pk,
							'rack' : rack.gmc_rack_id,
							})
				return HttpResponseRedirect(url)
		if 'rack-scanner' in request.POST:
			holding_rack_form = HoldingRackForm()
			sample_select_form = SampleSelectForm()
			rack_scan()
			rack_scanner = RackScanner.objects.filter(scanned_id=plate.holding_rack_id,
				acknowledged=False).order_by('-date_modified')
			if rack_scanner:
				rack_scanner_samples = RackScannerSample.objects.filter(rack_scanner=rack_scanner[0])
				samples_in_wrong_position = []
				extra_samples = []
				missing_samples = []
				for sample in plate_samples:
					found = False
					for rack_scanner_sample in rack_scanner_samples:
						if sample.laboratory_sample_id == rack_scanner_sample.sample_id:
							found = True
							if sample.plate_well_id == rack_scanner_sample.position:
								sample.sample_matched = True
								sample.save()
								rack_scanner_sample.matched = True
								rack_scanner_sample.save()
							else:
								samples_in_wrong_position.append(sample)
					if not found:
						missing_samples.append(sample)
				for rack_scanner_sample in rack_scanner_samples:
					if not rack_scanner_sample.matched:
						extra_samples.append(rack_scanner_sample)
				if samples_in_wrong_position or extra_samples or missing_samples:
					messages.error(request, "Scanned rack does not match with assigned rack wells for this rack!")
				else:
					messages.info(request, "Positions confirmed and correct.")
			else:
				messages.error(request, "Rack " + plate.holding_rack_id + " not found in Rack scanner CSV. Has the rack been scanned?")
		if 'ready' in request.POST:
			holding_rack_form = HoldingRackForm()
			sample_select_form = SampleSelectForm()
			pk = request.POST['ready']
			plate = Plate.objects.get(pk=pk)
			plate.ready_to_plate = True
			plate.save()
		if 'sample' in request.POST:
			holding_rack_form = HoldingRackForm()
			sample_select_form = SampleSelectForm(request.POST)
			if sample_select_form.is_valid():
				lab_sample_id = sample_select_form.cleaned_data.get('lab_sample_id')
				sample = None
				for unassigned_sample in samples:
					if unassigned_sample.laboratory_sample_id == lab_sample_id:
						sample = unassigned_sample
				if sample:
					print(sample.disease_area, sample.priority)
					if plate.disease_area == 'Unassigned':
						plate.disease_area = sample.disease_area
						plate.plate_type = sample.sample_type
						plate.priority = sample.priority
						plate.save()
					if sample.sample_type == plate.plate_type and sample.priority == plate.priority:
						well = request.POST['well']
						plate_manager.assign_well(request=request, sample=sample, well=well)
					else:
						messages.error(request, "Sample does not match holding rack type! Unable to add to this rack.")
				else:
					messages.error(request, lab_sample_id + " not found in GLH Rack " + rack.gmc_rack_id)
				url = reverse('plate_samples', kwargs={
							'gel1004' : rack.gel_1004_csv.pk,
							'rack' : rack.gmc_rack_id,
							'plate_id' : plate.holding_rack_id,
							})
				return HttpResponseRedirect(url)
	else:
		holding_rack_form = HoldingRackForm()
		sample_select_form = SampleSelectForm()
	return render(request, 'plate-samples.html', {"rack" : rack,
		"samples" : samples,
		"holding_rack_form" : holding_rack_form,
		"sample_select_form" : sample_select_form,
		"plate" : plate,
		"plate_samples" : plate_samples,
		"assigned_well_list" : assigned_well_list,
		"current_holding_racks_dict" : current_holding_racks_dict,
		"plate_rows": plate_rows,
		"plate_columns": plate_columns})

def ready_to_plate(request):
	"""
	Renders page displaying holding racks that are ready for plating
	"""
	ready_to_plate = Plate.objects.filter(ready_to_plate=True, plate_id__isnull=True)
	for plate in ready_to_plate:
		plate.sample_count = Sample.objects.filter(plate=plate).count
	return render(request, 'ready-to-plate.html', {"ready_to_plate" : ready_to_plate})

def plate_holding_rack(request, plate_pk):
	plate = Plate.objects.get(pk=plate_pk)
	samples = sorted(Sample.objects.filter(plate=plate), 
			key=lambda x: (x.plate_well_id[0], int(x.plate_well_id[1:])))
	if request.method == 'POST':
		if "rack-scanner" in request.POST:
			plating_form = PlatingForm()
			rack_scan()
			rack_scanner = RackScanner.objects.filter(scanned_id=plate.holding_rack_id,
				acknowledged=False).order_by('-date_modified')
			if rack_scanner:
				rack_scanner_samples = RackScannerSample.objects.filter(rack_scanner=rack_scanner[0])
				samples_in_wrong_position = []
				extra_samples = []
				missing_samples = []
				for sample in samples:
					found = False
					for rack_scanner_sample in rack_scanner_samples:
						if sample.laboratory_sample_id == rack_scanner_sample.sample_id:
							found = True
							if sample.plate_well_id == rack_scanner_sample.position:
								sample.sample_matched = True
								sample.save()
								rack_scanner_sample.matched = True
								rack_scanner_sample.save()
							else:
								samples_in_wrong_position.append(sample)
					if not found:
						missing_samples.append(sample)
				for rack_scanner_sample in rack_scanner_samples:
					if not rack_scanner_sample.matched:
						extra_samples.append(rack_scanner_sample)
				if samples_in_wrong_position or extra_samples or missing_samples:
					messages.error(request, "Scanned rack does not match with assigned rack wells for this rack!")
				else:
					plate.positions_confirmed = True
					plate.save()
					messages.info(request, "Positions confirmed and correct. Please plate samples and assign plate ID.")
			else:
				messages.error(request, "Rack " + plate.holding_rack_id + " not found in Plate/Rack scanner CSV. Has the rack been scanned?")
		if "assign-plate" in request.POST:
			plating_form = PlatingForm(request.POST)
			if plating_form.is_valid():
				plate_id = plating_form.cleaned_data.get('plate_id')
				plate.plate_id = plate_id
				plate.save()
	else:
		plating_form = PlatingForm()
	return render(request, 'plate-holding-rack.html', {
		"plate" : plate,
		"samples" : samples,
		"plating_form" : plating_form})

def ready_to_dispatch(request):
	"""
	Renders page displaying plates that are ready for dispatch
	"""
	ready_to_dispatch = Plate.objects.filter(ready_to_plate=True, plate_id__isnull=False, gel_1008_csv__isnull=True)
	for plate in ready_to_dispatch:
		plate.sample_count = Sample.objects.filter(plate=plate).count
	if request.method == 'POST':
		gel1008_form = Gel1008Form(request.POST)
		if gel1008_form.is_valid():
			if request.POST.getlist('selected_plate'):
				plate_pks = request.POST.getlist('selected_plate')
				consignment_number = gel1008_form.cleaned_data.get('consignment_number')
				date_of_dispatch = gel1008_form.cleaned_data.get('date_of_dispatch')
				directory = LoadConfig().load()['gel1008path']
				datetime_now = datetime.now(pytz.timezone('UTC'))
				filename = "ngis_bio_to_gel_sample_dispatch_" + datetime.now(pytz.timezone('UTC')).strftime("%y%m%d_%H%M%S") + ".csv"
				gel_1008_csv = Gel1008Csv.objects.create(
					filename = filename,
					report_generated_datetime = datetime_now,
					consignment_number = consignment_number,
					date_of_dispatch = date_of_dispatch)
				plates = []
				for pk in plate_pks:
					plate = Plate.objects.get(pk=pk)
					plate.gel_1008_csv = gel_1008_csv
					plate.save()
					plates.append(plate)
				path = directory + filename
				with open(path, 'w', newline='') as csvfile:
					writer = csv.writer(csvfile, delimiter=',',
						quotechar=',', quoting=csv.QUOTE_MINIMAL)
					writer.writerow(['Participant ID', 'Plate ID',
						'Normalised Biorepository Sample Volume', 'Normalised Biorepository Concentration',
						'Well ID', 'Plate Consignment Number', 'Plate Date of Dispatch'])
					for plate in plates:
						samples = Sample.objects.filter(plate=plate)
						for sample in samples:
							writer.writerow([sample.participant_id, plate.plate_id,
								sample.norm_biorep_sample_vol, sample.norm_biorep_conc,
								sample.plate_well_id, gel_1008_csv.consignment_number, gel_1008_csv.date_of_dispatch.replace(microsecond=0).isoformat().replace('+00:00', 'Z')])
				messages.info(request, "GEL1008 csv produced.")
			else:
				messages.warning(request, "No plates selected!")
			return HttpResponseRedirect('/ready-to-dispatch/')
	else:
		gel1008_form = Gel1008Form()
	return render(request, 'ready-to-dispatch.html', {
		"ready_to_dispatch" : ready_to_dispatch,
		"gel1008_form" : gel1008_form})

def audit(request):
	"""
	Renders the search results page. Users can also search again from this page.
	"""
	sample_select_form = SampleSelectForm()
	sample = None
	if request.method == 'POST':
		sample_select_form = SampleSelectForm(request.POST)
		if sample_select_form.is_valid():
			lab_sample_id = sample_select_form .cleaned_data.get('lab_sample_id')
			try:
				sample = Sample.objects.get(laboratory_sample_id=lab_sample_id)
			except:
				messages.error(request, "No samples found with laboratory ID " + lab_sample_id)
	return render(request, 'audit.html', {"sample_select_form" : sample_select_form,
		"sample" : sample})