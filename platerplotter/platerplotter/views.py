from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from platerplotter.models import (Gel1004Csv, Gel1005Csv, Gel1008Csv, ReceivingRack, Plate, 
	HoldingRack, Sample, RackScanner, RackScannerSample, HoldingRackWell)
from platerplotter.config.load_config import LoadConfig
from platerplotter.forms import (HoldingRackForm, SampleSelectForm, PlatingForm, 
	Gel1008Form, LogIssueForm, ResolveIssueForm)
from datetime import datetime
from django.core.exceptions import ValidationError
from platerplotter.holding_rack_manager import HoldingRackManager
import csv
import os
import pytz
import re
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4

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
	if 8 > len(rack_id) > 12:
		raise ValueError('Incorrect rack ID. Received {} which does not match the required specification.'.format(rack_id))
	else:
		return rack_id

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
	if is_proband == "TRUE" or is_proband == "True":
		return True
	if is_proband == "FALSE" or is_proband == "False":
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

@login_required()
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
									rack = ReceivingRack.objects.get(
										gel_1004_csv = gel_1004_csv,
										receiving_rack_id = check_rack_id(row[3].strip()),
										laboratory_id = check_laboratory_id(row[7].strip()))
								except:
									rack = ReceivingRack.objects.create(
										gel_1004_csv = gel_1004_csv,
										receiving_rack_id = check_rack_id(row[3].strip()),
										laboratory_id = check_laboratory_id(row[7].strip()),
										glh_sample_consignment_number = check_glh_sample_consignment_number(row[5].strip()))
								# creates new Sample object
								sample = Sample.objects.create(
									receiving_rack = rack,
									participant_id = check_participant_id(row[0].strip()),
									group_id = check_group_id(row[1].strip()),
									priority = check_priority(row[11].strip()),
									disease_area = check_disease_area(row[2].strip()),
									clin_sample_type = check_clinical_sample_type(row[4].strip()),
									laboratory_sample_id = check_laboratory_sample_id(row[6].strip()),
									laboratory_sample_volume = check_laboratory_sample_volume(row[8].strip()),
									receiving_rack_well = check_rack_well(row[9].strip()),
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
			racks = ReceivingRack.objects.filter(gel_1004_csv=gel_1004)
			directory = LoadConfig().load()['gel1005path']
			datetime_now = datetime.now(pytz.timezone('UTC'))
			filename = "ngis_bio_to_gel_samples_received_" + datetime.now(pytz.timezone('UTC')).strftime("%Y%m%d_%H%M%S") + ".csv"
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
					samples = Sample.objects.filter(receiving_rack=rack)
					for sample in samples:
						if sample.sample_received:
							sample_received = 'Yes'
						else:
							sample_received = 'No'
						received_datetime = ''
						if sample.sample_received_datetime:
							received_datetime = sample.sample_received_datetime.replace(microsecond=0).isoformat().replace('+00:00', 'Z')
						writer.writerow([sample.participant_id, rack.laboratory_id,
							sample_received, received_datetime,
							gel_1005.report_generated_datetime.replace(microsecond=0).isoformat().replace('+00:00', 'Z'), sample.laboratory_sample_id])
			return HttpResponseRedirect('/')
	unacked_gel_1004 = Gel1004Csv.objects.filter(gel_1005_csv__isnull = True)
	unacked_racks_dict = {}
	for gel_1004 in unacked_gel_1004:
		unacked_racks_dict[gel_1004] = ReceivingRack.objects.filter(gel_1004_csv=gel_1004)
		for gel_1004, racks in unacked_racks_dict.items():
			all_racks_acked = True
			for rack in racks:
				rack.no_samples = Sample.objects.filter(receiving_rack=rack).count()
				if not rack.rack_acknowledged:
					all_racks_acked = False
			gel_1004.all_racks_acked = all_racks_acked
	return render(request, 'platerplotter/import-acks.html', {"unacked_racks_dict" : unacked_racks_dict})

@login_required()
def acknowledge_samples(request, gel1004, rack):
	rack = ReceivingRack.objects.get(gel_1004_csv=gel1004, receiving_rack_id=rack)
	samples = Sample.objects.filter(receiving_rack=rack)
	sample_select_form = SampleSelectForm()
	log_issue_form = LogIssueForm()
	sample_form_dict = {}
	for sample in samples:
		sample_form_dict[sample] = LogIssueForm(instance=sample)
	if request.method == 'POST':
		if 'rack-scanner' in request.POST:
			rack_scan()
			rack_scanner = RackScanner.objects.filter(scanned_id=rack.receiving_rack_id,
				acknowledged=False).order_by('-date_modified')
			if rack_scanner:
				rack_scanner_samples = RackScannerSample.objects.filter(rack_scanner=rack_scanner[0])
				samples_received_wrong_position = []
				extra_samples = []
				for sample in samples:
					for rack_scanner_sample in rack_scanner_samples:
						if sample.laboratory_sample_id == rack_scanner_sample.sample_id:
							if sample.receiving_rack_well == rack_scanner_sample.position:
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
				for rack_scanner_item in rack_scanner:
					rack_scanner_item.acknowledged = True
					rack_scanner_item.save()
			else:
				messages.error(request, "Rack " + rack.receiving_rack_id + " not found in Plate/Rack scanner CSV. Has the rack been scanned?")
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
					sample = Sample.objects.get(receiving_rack=rack, laboratory_sample_id=lab_sample_id)
				except:
					messages.error(request, "Sample " + lab_sample_id + " does not exist")
				if sample:
					sample.sample_received = True
					sample.sample_received_datetime = datetime.now(pytz.timezone('UTC'))
					sample.save()
			sample_select_form = SampleSelectForm()
			log_issue_form = LogIssueForm()
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
				"rack" : rack.receiving_rack_id,
				})
			return HttpResponseRedirect(url)
		if 'log-issue' in request.POST:
			log_issue_form = LogIssueForm(request.POST)
			if log_issue_form.is_valid():
				pk = request.POST['log-issue']
				comment = log_issue_form.cleaned_data.get('comment')
				sample = Sample.objects.get(pk=pk)
				sample.issue_identified = True
				sample.comment = comment
				sample.issue_outcome = "Not resolved"
				sample.save()
				url = reverse('acknowledge_samples', kwargs={
					"gel1004" : gel1004,
					"rack" : rack.receiving_rack_id,
					})
				return HttpResponseRedirect(url)
		if 'delete-issue' in request.POST:
			log_issue_form = LogIssueForm(request.POST)
			if log_issue_form.is_valid():
				pk = request.POST['delete-issue']
				sample = Sample.objects.get(pk=pk)
				sample.issue_identified = False
				sample.comment = None
				sample.save()
				url = reverse('acknowledge_samples', kwargs={
					"gel1004" : gel1004,
					"rack" : rack.receiving_rack_id,
					})
				return HttpResponseRedirect(url)
	all_samples_received = True
	for sample in samples:
		if not sample.sample_received:
			all_samples_received = False
	if all_samples_received:
		messages.info(request, "All samples received")
	return render(request, 'platerplotter/acknowledge-samples.html', {"rack" : rack,
		"samples" : samples,
		"sample_select_form" : sample_select_form,
		"sample_form_dict" : sample_form_dict,
		"log_issue_form" : log_issue_form,
		"all_samples_received" : all_samples_received})

@login_required()
def problem_samples(request, holding_rack_id=None):
	holding_rack_rows = ['A','B','C','D','E','F','G','H']
	holding_rack_columns = ['01','02','03','04','05','06','07','08','09','10','11','12']
	samples = Sample.objects.filter(issue_identified = True, issue_outcome= "Not resolved").exclude(holding_rack_well__holding_rack__holding_rack_type='Problem')
	sample_form_dict = {}
	for sample in samples:
		sample_form_dict[sample] = LogIssueForm(instance=sample)
	current_holding_racks = HoldingRack.objects.filter(holding_rack_type="Problem")
	current_holding_racks_dict = {}
	for current_holding_rack in current_holding_racks:
		current_holding_racks_dict[current_holding_rack] = Sample.objects.filter(holding_rack_well__holding_rack=current_holding_rack).count()
	assigned_well_list = []
	holding_rack_samples_form_dict = {}
	if holding_rack_id:
		holding_rack = HoldingRack.objects.get(holding_rack_id=holding_rack_id, holding_rack_type='Problem', plate__isnull=True)
		holding_rack_samples = Sample.objects.filter(holding_rack_well__holding_rack=holding_rack)
		holding_rack_manager = HoldingRackManager(holding_rack)
		for sample in holding_rack_samples:
			assigned_well_list.append(sample.holding_rack_well.well_id)
			holding_rack_samples_form_dict[sample] = ResolveIssueForm(instance=sample)
	else:
		holding_rack = None
		holding_rack_samples = None
	if request.method == 'POST':
		if 'holding' in request.POST:
			sample_select_form = SampleSelectForm()
			holding_rack_form = HoldingRackForm(request.POST)
			if holding_rack_form.is_valid():
				error = False
				holding_rack_id = holding_rack_form.cleaned_data.get('holding_rack_id')
				try:
					holding_rack = HoldingRack.objects.get(holding_rack_id=holding_rack_id, plate__isnull=True)
					if holding_rack.holding_rack_type != "Problem":
						messages.error(request, "You have scanned a holding rack being used for " + holding_rack.holding_rack_type + " samples. Please scan an exisiting or new Problem rack.")
						error = True
				except:
					holding_rack = HoldingRack.objects.create(holding_rack_id=holding_rack_id, holding_rack_type="Problem")
					for holding_rack_row in holding_rack_rows:
						for holding_rack_column in holding_rack_columns:
							HoldingRackWell.objects.create(holding_rack=holding_rack,
								well_id=holding_rack_row + holding_rack_column)
				if holding_rack and not error:
					url = reverse('problem_samples', kwargs={
							'holding_rack_id' : holding_rack.holding_rack_id,
							})
				else:
					url = reverse('problem_samples')
				return HttpResponseRedirect(url)
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
					well = request.POST['well']
					holding_rack_manager.assign_well(request=request, sample=sample, well=well)
				else:
					messages.error(request, lab_sample_id + " not found. Has an issue been logged for this sample?")
				url = reverse('problem_samples', kwargs={
							'holding_rack_id' : holding_rack.holding_rack_id,
							})
				return HttpResponseRedirect(url)
		if 'log-issue' in request.POST:
			log_issue_form = LogIssueForm(request.POST)
			if log_issue_form.is_valid():
				pk = request.POST['log-issue']
				comment = log_issue_form.cleaned_data.get('comment')
				sample = Sample.objects.get(pk=pk)
				sample.issue_identified = True
				sample.comment = comment
				sample.issue_outcome = "Not resolved"
				sample.save()
				url = reverse('problem_samples')
				return HttpResponseRedirect(url)
		if 'delete-issue' in request.POST:
			log_issue_form = LogIssueForm(request.POST)
			if log_issue_form.is_valid():
				pk = request.POST['delete-issue']
				sample = Sample.objects.get(pk=pk)
				sample.issue_identified = False
				sample.comment = None
				sample.issue_outcome = None
				sample.save()
				url = reverse('problem_samples')
				return HttpResponseRedirect(url)
		if 'resolve-issue' in request.POST:
			resolve_issue_form = ResolveIssueForm(request.POST)
			if resolve_issue_form.is_valid():
				pk = request.POST['resolve-issue']
				comment = resolve_issue_form.cleaned_data.get('comment')
				outcome = resolve_issue_form.cleaned_data.get('issue_outcome')
				sample = Sample.objects.get(pk=pk)
				sample.comment = comment
				sample.issue_outcome = outcome
				if outcome == "Sample returned to extracting GLH" or outcome == "Sample destroyed":
					sample.holding_rack_well.delete()
				sample.save()
				url = reverse('problem_samples', kwargs={
							'holding_rack_id' : holding_rack.holding_rack_id,
							})
				return HttpResponseRedirect(url)
	else:
		holding_rack_form = HoldingRackForm()
		sample_select_form = SampleSelectForm()

	return render(request, 'platerplotter/problem-samples.html', {"sample_form_dict" : sample_form_dict,
		"holding_rack_form" : holding_rack_form,
		"sample_select_form" : sample_select_form,
		"holding_rack" : holding_rack,
		"holding_rack_samples" : holding_rack_samples,
		"holding_rack_samples_form_dict" : holding_rack_samples_form_dict,
		"assigned_well_list" : assigned_well_list,
		"current_holding_racks_dict" : current_holding_racks_dict,
		"holding_rack_rows": holding_rack_rows,
		"holding_rack_columns": holding_rack_columns})


@login_required()
def awaiting_holding_rack_assignment(request):
	unplated_samples = Sample.objects.filter(holding_rack_well__isnull = True, 
		receiving_rack__gel_1004_csv__gel_1005_csv__isnull = False,
		sample_received = True, issue_identified=False)
	unplated_racks_dict = {}
	for sample in unplated_samples:
		if sample.receiving_rack in unplated_racks_dict:
			unplated_racks_dict[sample.receiving_rack].append(sample)
		else:
			unplated_racks_dict[sample.receiving_rack] = [sample] 
	for rack, samples in unplated_racks_dict.items():
		disease_area_set = set()
		rack_type_set = set()
		priority_set = set()
		for sample in samples:
			disease_area_set.add(sample.disease_area)
			rack_type_set.add(sample.sample_type)
			priority_set.add(sample.priority)
		if len(disease_area_set) == 1:
			rack.disease_area = disease_area_set.pop()
		else:
			rack.disease_area = 'Mixed'
		if len(rack_type_set) == 1:
			rack.holding_rack_type = rack_type_set.pop()
		else:
			rack.holding_rack_type = 'Mixed'
		if len(priority_set) == 1:
			rack.priority = priority_set.pop()
		else:
			rack.priority = 'Mixed'
		rack.save()
	problem_samples = Sample.objects.filter(holding_rack_well__holding_rack__holding_rack_type="Problem", issue_outcome="Ready for plating")
	problem_holding_rack_dict = {}
	for problem_sample in problem_samples:
		if problem_sample.holding_rack_well.holding_rack in problem_holding_rack_dict:
			problem_holding_rack_dict[problem_sample.holding_rack_well.holding_rack].append(sample)
		else:
			problem_holding_rack_dict[problem_sample.holding_rack_well.holding_rack] = [problem_sample]
	return render(request, 'platerplotter/awaiting-holding-rack-assignment.html', {
		"unplated_racks_dict" : unplated_racks_dict,
		"problem_holding_rack_dict" : problem_holding_rack_dict})

@login_required()
def assign_samples_to_holding_rack(request, rack, gel1004=None, holding_rack_id=None):
	print(holding_rack_id)
	holding_rack_rows = ['A','B','C','D','E','F','G','H']
	holding_rack_columns = ['01','02','03','04','05','06','07','08','09','10','11','12']
	if gel1004:
		rack = ReceivingRack.objects.get(gel_1004_csv=gel1004, receiving_rack_id=rack)
		samples = Sample.objects.filter(receiving_rack=rack,
			holding_rack_well__isnull = True,
			receiving_rack__gel_1004_csv__gel_1005_csv__isnull = False,
			sample_received = True).exclude(issue_outcome="Not resolved").exclude(
											issue_outcome="Sample returned to extracting GLH").exclude(
											issue_outcome="Sample destroyed")
		problem_holding_rack=None
	else:
		problem_holding_rack = HoldingRack.objects.get(holding_rack_id=rack, holding_rack_type='Problem')
		samples = Sample.objects.filter(holding_rack_well__holding_rack=problem_holding_rack, issue_outcome="Ready for plating")
		rack=None
	sample_form_dict = {}
	for sample in samples:
		sample_form_dict[sample] = LogIssueForm(instance=sample)
	current_holding_racks = HoldingRack.objects.filter(plate__isnull=True).exclude(holding_rack_type='Problem')
	current_holding_racks_dict = {}
	for current_holding_rack in current_holding_racks:
		current_holding_racks_dict[current_holding_rack] = Sample.objects.filter(holding_rack_well__holding_rack=current_holding_rack).count()
	assigned_well_list = []
	holding_rack_samples_form_dict = {}
	if holding_rack_id:
		holding_rack = HoldingRack.objects.get(holding_rack_id=holding_rack_id, plate__isnull=True)
		holding_rack_samples = Sample.objects.filter(holding_rack_well__holding_rack=holding_rack)
		holding_rack_manager = HoldingRackManager(holding_rack)
		for sample in holding_rack_samples:
			assigned_well_list.append(sample.holding_rack_well.well_id)
			holding_rack_samples_form_dict[sample] = LogIssueForm(instance=sample)
	else:
		holding_rack = None
		holding_rack_samples = None
	print(holding_rack)
	if request.method == 'POST':
		if 'holding' in request.POST:
			sample_select_form = SampleSelectForm()
			holding_rack_form = HoldingRackForm(request.POST)
			if holding_rack_form.is_valid():
				error = False
				holding_rack_id = holding_rack_form.cleaned_data.get('holding_rack_id')
				if holding_rack_id == rack.receiving_rack_id:
					messages.error(request, "You have scanned the GMC Rack. Please scan the holding rack.")
				else:
					try:
						holding_rack = HoldingRack.objects.get(holding_rack_id=holding_rack_id, plate__isnull=True)
						if holding_rack.holding_rack_type == 'Problem':
							messages.error(request, "You have scanned a holding rack for Problem samples. Please scan the correct holding rack.")
							error = True
					except:
						holding_rack = HoldingRack.objects.create(holding_rack_id=holding_rack_id)
						for holding_rack_row in holding_rack_rows:
							for holding_rack_column in holding_rack_columns:
								HoldingRackWell.objects.create(holding_rack=holding_rack,
									well_id=holding_rack_row + holding_rack_column)
				if holding_rack and not error:
					url = reverse('assign_samples_to_holding_rack', kwargs={
							'gel1004' : rack.gel_1004_csv.pk,
							'rack' : rack.receiving_rack_id,
							'holding_rack_id' : holding_rack.holding_rack_id,
							})
				else:
					url = reverse('assign_samples_to_holding_rack', kwargs={
							'gel1004' : rack.gel_1004_csv.pk,
							'rack' : rack.receiving_rack_id,
							})
				return HttpResponseRedirect(url)
		if 'rack-scanner' in request.POST:
			holding_rack_form = HoldingRackForm()
			sample_select_form = SampleSelectForm()
			rack_scan()
			rack_scanner = RackScanner.objects.filter(scanned_id=holding_rack.holding_rack_id,
				acknowledged=False).order_by('-date_modified')
			if rack_scanner:
				rack_scanner_samples = RackScannerSample.objects.filter(rack_scanner=rack_scanner[0])
				samples_in_wrong_position = []
				extra_samples = []
				missing_samples = []
				for sample in holding_rack_samples:
					found = False
					for rack_scanner_sample in rack_scanner_samples:
						if sample.laboratory_sample_id == rack_scanner_sample.sample_id:
							found = True
							if sample.holding_rack_well.well_id == rack_scanner_sample.position:
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
				for rack_scanner_item in rack_scanner:
					rack_scanner_item.acknowledged = True
					rack_scanner_item.save()
			else:
				messages.error(request, "Rack " + holding_rack.holding_rack_id + " not found in Rack scanner CSV. Has the rack been scanned?")
		if 'ready' in request.POST:
			holding_rack_form = HoldingRackForm()
			sample_select_form = SampleSelectForm()
			pk = request.POST['ready']
			holding_rack = HoldingRack.objects.get(pk=pk)
			# assign buffer wells
			holding_rack_manager.assign_buffer()
			buffer_wells = HoldingRackWell.objects.filter(holding_rack=holding_rack, buffer_added = True).order_by('well_id')
			holding_rack.ready_to_plate = True
			holding_rack.save()
			messages.info(request, "Holding rack has been marked as ready for plating.")
			if buffer_wells:
				buffer_wells_list = ''
				for buffer_well in buffer_wells:
					buffer_wells_list += buffer_well.well_id + ', '
				messages.warning(request, "Buffer will need to be added to the following wells during plating: " + buffer_wells_list)
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
					if holding_rack.disease_area == 'Unassigned':
						holding_rack.disease_area = sample.disease_area
						holding_rack.holding_rack_type = sample.sample_type
						holding_rack.priority = sample.priority
						holding_rack.save()
					if sample.sample_type == holding_rack.holding_rack_type and sample.priority == holding_rack.priority:
						well = request.POST['well']
						holding_rack_manager.assign_well(request=request, sample=sample, well=well)
					else:
						messages.error(request, "Sample does not match holding rack type! Unable to add to this rack.")
				else:
					messages.error(request, lab_sample_id + " not found in GLH Rack " + rack.receiving_rack_id)
				if problem_holding_rack:
					url = reverse('assign_problem_samples_to_holding_rack', kwargs={
								'rack' : problem_holding_rack.holding_rack_id,
								'holding_rack_id' : holding_rack.holding_rack_id,
								})
				else:	
					url = reverse('assign_samples_to_holding_rack', kwargs={
								'gel1004' : rack.gel_1004_csv.pk,
								'rack' : rack.receiving_rack_id,
								'holding_rack_id' : holding_rack.holding_rack_id,
								})
				return HttpResponseRedirect(url)
		if 'log-issue' in request.POST:
			log_issue_form = LogIssueForm(request.POST)
			if log_issue_form.is_valid():
				pk = request.POST['log-issue']
				comment = log_issue_form.cleaned_data.get('comment')
				sample = Sample.objects.get(pk=pk)
				sample.issue_identified = True
				sample.comment = comment
				sample.issue_outcome = "Not resolved"
				sample.save()
				if problem_holding_rack:
					if holding_rack:
						url = reverse('assign_problem_samples_to_holding_rack', kwargs={
									'rack' : problem_holding_rack.holding_rack_id,
									'holding_rack_id' : holding_rack.holding_rack_id,
									})
					else:
						url = reverse('assign_problem_samples_to_holding_rack', kwargs={
									'rack' : problem_holding_rack.holding_rack_id,
									})
				else:
					if holding_rack:	
						url = reverse('assign_samples_to_holding_rack', kwargs={
									'gel1004' : rack.gel_1004_csv.pk,
									'rack' : rack.receiving_rack_id,
									'holding_rack_id' : holding_rack.holding_rack_id,
									})
					else:
						url = reverse('assign_samples_to_holding_rack', kwargs={
									'gel1004' : rack.gel_1004_csv.pk,
									'rack' : rack.receiving_rack_id,
									})
				return HttpResponseRedirect(url)
	else:
		holding_rack_form = HoldingRackForm()
		sample_select_form = SampleSelectForm()
	return render(request, 'platerplotter/assign-samples-to-holding-rack.html', {
		"rack" : rack,
		"problem_holding_rack" : problem_holding_rack,
		"samples" : samples,
		"holding_rack_form" : holding_rack_form,
		"sample_select_form" : sample_select_form,
		"sample_form_dict" : sample_form_dict,
		"holding_rack" : holding_rack,
		"holding_rack_samples" : holding_rack_samples,
		"holding_rack_samples_form_dict" : holding_rack_samples_form_dict,
		"assigned_well_list" : assigned_well_list,
		"current_holding_racks_dict" : current_holding_racks_dict,
		"holding_rack_rows": holding_rack_rows,
		"holding_rack_columns": holding_rack_columns})

@login_required()
def ready_to_plate(request):
	"""
	Renders page displaying holding racks that are ready for plating
	"""
	ready_to_plate = HoldingRack.objects.filter(ready_to_plate=True, plate__isnull=True)
	for rack in ready_to_plate:
		rack.sample_count = Sample.objects.filter(holding_rack_well__holding_rack=rack).count
	return render(request, 'platerplotter/ready-to-plate.html', {"ready_to_plate" : ready_to_plate})

@login_required()
def plate_holding_rack(request, holding_rack_pk):
	holding_rack = HoldingRack.objects.get(pk=holding_rack_pk)
	samples = Sample.objects.filter(holding_rack_well__holding_rack=holding_rack)
	if request.method == 'POST':
		if "rack-scanner" in request.POST:
			plating_form = PlatingForm()
			rack_scan()
			rack_scanner = RackScanner.objects.filter(scanned_id=holding_rack.holding_rack_id,
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
							if sample.holding_rack_well.well_id == rack_scanner_sample.position:
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
					holding_rack.positions_confirmed = True
					holding_rack.save()
					messages.info(request, "Positions confirmed and correct. Please plate samples and assign plate ID.")
				for rack_scanner_item in rack_scanner:
					rack_scanner_item.acknowledged = True
					rack_scanner_item.save()
			else:
				messages.error(request, "Rack " + holding_rack.holding_rack_id + " not found in Plate/Rack scanner CSV. Has the rack been scanned?")
		if "assign-plate" in request.POST:
			plating_form = PlatingForm(request.POST)
			if plating_form.is_valid():
				plate_id = plating_form.cleaned_data.get('plate_id')
				plate = Plate.objects.create(plate_id = plate_id)
				holding_rack.plate = plate
				holding_rack.save()
				# generate output for robot
				holding_rack_wells = HoldingRackWell.objects.filter(holding_rack=holding_rack).order_by('well_id')
				for well in holding_rack_wells:
					print(well.well_id)
	else:
		plating_form = PlatingForm()
	return render(request, 'platerplotter/plate-holding-rack.html', {
		"holding_rack" : holding_rack,
		"samples" : samples,
		"plating_form" : plating_form})

@login_required()
def ready_to_dispatch(request):
	"""
	Renders page displaying plates that are ready for dispatch
	"""
	ready_to_dispatch = HoldingRack.objects.filter(ready_to_plate=True, plate__isnull=False, plate__gel_1008_csv__isnull=True)
	for holding_rack in ready_to_dispatch:
		holding_rack.sample_count = Sample.objects.filter(holding_rack_well__holding_rack=holding_rack).count
	if request.method == 'POST':
		gel1008_form = Gel1008Form(request.POST)
		if gel1008_form.is_valid():
			if request.POST.getlist('selected_plate'):
				plate_pks = request.POST.getlist('selected_plate')
				consignment_number = gel1008_form.cleaned_data.get('consignment_number')
				date_of_dispatch = gel1008_form.cleaned_data.get('date_of_dispatch')
				directory = LoadConfig().load()['gel1008path']
				datetime_now = datetime.now(pytz.timezone('UTC'))
				filename = "ngis_bio_to_gel_sample_dispatch_" + datetime.now(pytz.timezone('UTC')).strftime("%Y%m%d_%H%M%S") + ".csv"
				gel_1008_csv = Gel1008Csv.objects.create(
					filename = filename,
					report_generated_datetime = datetime_now,
					consignment_number = consignment_number,
					date_of_dispatch = date_of_dispatch)
				holding_racks = []
				for pk in plate_pks:
					plate = Plate.objects.get(pk=pk)
					plate.gel_1008_csv = gel_1008_csv
					plate.save()
					holding_racks.append(plate.holding_rack)
				path = directory + filename
				doc = SimpleDocTemplate(path[:-3] + 'pdf')
				doc.pagesize = landscape(A4)
				elements = []
				data = [['Participant ID', 'Laboratory Sample ID', 'Plate ID', 'Well ID', 
						'Plate Consignment Number', 'Plate Date of Dispatch']]
				with open(path, 'w', newline='') as csvfile:
					writer = csv.writer(csvfile, delimiter=',',
						quotechar=',', quoting=csv.QUOTE_MINIMAL)
					writer.writerow(['Participant ID', 'Laboratory Sample ID', 'Plate ID',
						'Normalised Biorepository Sample Volume', 'Normalised Biorepository Concentration',
						'Well ID', 'Plate Consignment Number', 'Plate Date of Dispatch'])
					for holding_rack in holding_racks:
						samples = Sample.objects.filter(holding_rack_well__holding_rack=holding_rack).order_by('holding_rack_well__well_id')
						for sample in samples:
							writer.writerow([sample.participant_id, sample.laboratory_sample_id, 
								sample.holding_rack_well.holding_rack.plate.plate_id,
								sample.norm_biorep_sample_vol, sample.norm_biorep_conc,
								sample.holding_rack_well.well_id, gel_1008_csv.consignment_number, 
								gel_1008_csv.date_of_dispatch.replace(microsecond=0).isoformat().replace('+00:00', 'Z')])
							data.append([sample.participant_id, sample.laboratory_sample_id,
								sample.holding_rack_well.holding_rack.plate.plate_id,
								sample.holding_rack_well.well_id, gel_1008_csv.consignment_number, 
								gel_1008_csv.date_of_dispatch.replace(microsecond=0).isoformat().replace('+00:00', 'Z')])
				flowObjects = list()
				styles=getSampleStyleSheet()
				table_header = "Sample summary for consignment: " + str(consignment_number)
				flowObjects.append(Paragraph(table_header,styles["h4"]))
				t1=Table(data,hAlign="LEFT")
				t1.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
							('BOX', (0,0), (-1,-1), 0.25, colors.black),
							('BACKGROUND',(0,0),(-1,0),colors.gray),
							('TEXTCOLOR',(0,0),(-1,0),colors.black),
							]))
				flowObjects.append(t1)
				doc.build(flowObjects)

				messages.info(request, "GEL1008 csv produced.")
			else:
				messages.warning(request, "No plates selected!")
			return HttpResponseRedirect('/ready-to-dispatch/')
	else:
		gel1008_form = Gel1008Form()
	return render(request, 'platerplotter/ready-to-dispatch.html', {
		"ready_to_dispatch" : ready_to_dispatch,
		"gel1008_form" : gel1008_form})

@login_required()
def audit(request):
	"""
	Renders the audit page showing all processed samples. 
	"""
	samples = Sample.objects.all().prefetch_related('receiving_rack', 'holding_rack_well', 
				'holding_rack_well__holding_rack', 'holding_rack_well__holding_rack__plate', 
				'holding_rack_well__holding_rack__plate__gel_1008_csv', 
				'receiving_rack__gel_1004_csv', 'receiving_rack__gel_1004_csv__gel_1005_csv')
	return render(request, 'platerplotter/audit.html', {"samples" : samples})



def register(request):
    created = False
    matching_users = []
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        matching_users = User.objects.filter(username=username)
        if not matching_users:
            u = User.objects.create_user(username, email, password)
            u.is_active = False
            u.save()
            created = True
    return render(request, 'registration/register.html', {'created': created, 'matching_users': matching_users})