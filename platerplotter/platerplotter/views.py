from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse, Http404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from platerplotter.models import (Gel1004Csv, Gel1005Csv, Gel1008Csv, ReceivingRack, Plate, 
	HoldingRack, Sample, RackScanner, RackScannerSample, HoldingRackWell)
from platerplotter.config.load_config import LoadConfig
from platerplotter.forms import (HoldingRackForm, SampleSelectForm, PlatingForm, 
	Gel1008Form, LogIssueForm, ResolveIssueForm, PlateSelectForm)
from datetime import datetime
from django.core.exceptions import ValidationError
from platerplotter.holding_rack_manager import HoldingRackManager
import csv
import os
import pytz
import re
import time
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from pathlib import Path

# def ajax_change_sample_received_status(request):
#	 sample_received = request.GET.get('sample_received', False)
#	 sample_id = request.GET.get('sample_id', False)
#	 # first you get your Job model
#	 sample = Sample.objects.get(pk=sample_id)
#	 try:
#		 sample.sample_received = sample_received
#		 sample.save()
#		 return JsonResponse({"success": True})
#	 except Exception as e:
#		 return JsonResponse({"success": False})
#	 return JsonResponse(data)

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

def strip_zeros(well):
	if well[1] == '0':
		return well[0] + well[2]
	else:
		return well

def check_plating_organisation(plating_organisation):
	error = None
	if plating_organisation.lower() != 'wwm':
		error = 'Plating orgnaisation entered as {}. Expected "wmm".'.format(plating_organisation.lower())
	return plating_organisation.lower(), error

def check_rack_id(rack_id):
	error = None
	if 8 > len(rack_id) or len(rack_id) > 12:
		error = 'Incorrect rack ID. Received {} which does not match the required specification.'.format(rack_id)
	return rack_id, error

def check_laboratory_id(laboratory_id):
	error = None
	accepted_ids = ["yne", "now", "eme", "lnn", "lns", "wwm", "sow"]
	if laboratory_id.lower() not in accepted_ids:
		error = 'Incorrect laboratory ID. Received {} which is not on the list of accepted laboratory IDs.'.format(laboratory_id)
	return laboratory_id.lower(), error

def check_participant_id(participant_id):
	error = None
	if not re.match(r'^p\d{11}$', participant_id.lower()):
		error = 'Incorrect participant ID. Received {} which does not match the required specification.'.format(participant_id)
	return participant_id.lower(), error

def check_group_id(group_id):
	error = None
	if not re.match(r'^r\d{11}$', group_id.lower()):
		error = 'Incorrect group ID. Received {} which does not match the required specification.'.format(group_id)
	return group_id.lower(), error

def check_priority(priority):
	error = None
	accepted_values = ['Urgent', 'Routine']
	if priority.title() not in accepted_values:
		error = 'Incorrect priority. Received {}. Must be either routine or urgent.'.format(priority)
	return priority.title(), error

def check_disease_area(disease_area):
	error = None
	accepted_values = ['Cancer', 'Rare Disease']
	if disease_area.title() not in accepted_values:
		error = 'Incorrect disease area. Received {}. Must be either cancer or rare disease.'.format(disease_area)
	return disease_area.title(), error

def check_clinical_sample_type(clin_sample_type):
	error = None
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
		error = 'Clinical sample type not in list of accepted values. Received {}.'.format(clin_sample_type)
	return clin_sample_type.lower(), error

def check_glh_sample_consignment_number(glh_sample_consignment_number):
	error = None
	if not re.match(r'^[a-z]{3}-\d{4}-\d{2}-\d{2}-\d{2}-[1,2]$', glh_sample_consignment_number.lower()) and not re.match(
		r'^[a-z]{3}-\d{4}-\d{2}-\d{2}-[1,2]$', glh_sample_consignment_number.lower()) and not re.match(
		r'^.*$', glh_sample_consignment_number.lower()):
		error = 'Incorrect GLH sample consignment number. Received {} which does not match the required specification.'.format(glh_sample_consignment_number)
	return glh_sample_consignment_number.lower(), error

def check_laboratory_sample_id(laboratory_sample_id):
	error = None
	if not re.match(r'^\d{10}$', laboratory_sample_id):
		error = 'Incorrect laboratory sample ID. Received {}. Should be 10 digits'.format(laboratory_sample_id)
	return laboratory_sample_id, error

def check_laboratory_sample_volume(laboratory_sample_volume):
	error = None
	if not re.match(r'^\d*$', laboratory_sample_volume):
		error = 'Incorrect laboratory sample volume. Received {}. Should be all digits'.format(laboratory_sample_volume)
	return laboratory_sample_volume, error

def check_rack_well(rack_well):
	error = None
	if not re.match(r'^[A-H](01|02|03|04|05|06|07|08|09|10|11|12)$', rack_well.upper()):
		error = 'Invalid rack well for a 96 well rack. Received {}.'.format(rack_well)
	return rack_well.upper(), error

def check_is_proband(is_proband):
	error = None
	if is_proband == "TRUE" or is_proband == "True":
		return True, error
	if is_proband == "FALSE" or is_proband == "False":
		return False, error
	if type(is_proband) == type(True):
		return is_proband, error
	else:
		error = 'Invalid value for Is Proband. Received {} but expected a boolean value'.format(is_proband)
		return is_proband, error

def check_is_repeat(is_repeat):
	error = None
	accepted_values = ['New', 'Retrospective', 'Repeat New', 'Repeat Retrospective']
	if is_repeat.title() not in accepted_values:
		error = 'Is repeat field not in list of accepted values. Received {}.'.format(is_repeat)
	return is_repeat.title(), error

def check_tissue_type(tissue_type):
	error = None
	accepted_values = ["Normal or Germline sample", "Liquid tumour sample", "Solid tumour sample", "Abnormal tissue sample", "Omics sample"]
	if tissue_type not in accepted_values:
		error = 'Tissue type not in list of accepted values. Received {}.'.format(tissue_type)
	return tissue_type, error

def check_rack_type(rack_type):
	error = None
	accepted_values = ['CG', 'CT', 'RF', 'RP']
	if rack_type not in accepted_values:
		error = 'Rack type not in list of accepted_values. Received {}.'.format(rack_type)
	return rack_type, error

def old_rack_scan(test_status=False):
	if test_status:
		directory = str(Path.cwd().parent) + '/TestData/Inbound/RackScanner/'
	else:	
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

def rack_scan(test_status=False):
	if test_status:
		directory = str(Path.cwd().parent) + '/TestData/Inbound/RackScanner/'
	else:	
		directory = LoadConfig().load()['rack_scanner_path']
	for filename in os.listdir(directory):
		if filename.endswith(".csv"):
			path = directory + filename
			date_modified = datetime.fromtimestamp(os.path.getmtime(path), pytz.timezone('UTC'))
			with open(path, 'r') as csvFile:
				reader = csv.reader(csvFile, delimiter=',', skipinitialspace=True)
				for row in reader:
					if row[2] != '':
						rack_scanner, created = RackScanner.objects.get_or_create(
							filename=filename,
							scanned_id=row[0].strip(),
							date_modified=date_modified)
						RackScannerSample.objects.get_or_create(rack_scanner=rack_scanner,
							sample_id=row[2].strip(),
							position=pad_zeros(row[1].strip()))
			os.rename(path, directory + "processed/" + filename)


def confirm_sample_positions(request, rack, rack_samples, first_check=False, 
							final_check=False, test_status=False):
	rack_scan(test_status=test_status)
	if first_check:
		rack_id = rack.receiving_rack_id
	else:
		rack_id = rack.holding_rack_id
	rack_scanner = RackScanner.objects.filter(scanned_id=rack_id,
			acknowledged=False).order_by('-date_modified')
	if rack_scanner:
		rack_scanner_samples = RackScannerSample.objects.filter(rack_scanner=rack_scanner[0])
		samples_in_wrong_position = []
		extra_samples = []
		missing_samples = []
		for sample in rack_samples:
			found = False
			for rack_scanner_sample in rack_scanner_samples:
				if sample.laboratory_sample_id == rack_scanner_sample.sample_id:
					found = True
					rack_scanner_sample.matched = True
					rack_scanner_sample.save()
					if first_check:
						if sample.receiving_rack_well == rack_scanner_sample.position:
							sample.sample_received = True
							sample.sample_received_datetime = datetime.now(pytz.timezone('UTC'))
							sample.save()
						else:
							samples_in_wrong_position.append((sample, rack_scanner_sample.position))
					else:
						if sample.holding_rack_well.well_id == rack_scanner_sample.position:
							if final_check:
								sample.sample_matched = True
								sample.save()
						else:
							samples_in_wrong_position.append((sample, rack_scanner_sample.position))
			if not found:
				missing_samples.append(sample)
		for rack_scanner_sample in rack_scanner_samples:
			if not rack_scanner_sample.matched:
				extra_samples.append(rack_scanner_sample)
		if samples_in_wrong_position or extra_samples or missing_samples:
			wrong = ''
			missing = ''
			extra = ''
			if samples_in_wrong_position:
				wrong = 'The following samples are in the wrong positions:<ul>'
				for sample, wrong_position in samples_in_wrong_position:
					if first_check:
						sample_well = sample.receiving_rack_well
					else:
						sample_well = sample.holding_rack_well.well_id
					wrong += "<li>" + sample.laboratory_sample_id + " found in well " + wrong_position + \
					" but should be in well " + sample_well + "</li>"
				wrong += "</ul>"
			if missing_samples:
				missing = 'The following samples are missing from the holding rack:<ul>'
				for sample in missing_samples:
					if first_check:
						sample_well = sample.receiving_rack_well
					else:
						sample_well = sample.holding_rack_well.well_id
					missing += "<li>" + sample.laboratory_sample_id + " was expected in well " + \
					sample_well + " but it was not found in the holding rack </li>"
				missing += "</ul>"
			if extra_samples:
				extra = 'The following extra samples are in the holding rack but were not expected:<ul>'
				for sample in extra_samples:
					extra += "<li>" + sample.sample_id + " found in well " + sample.position + \
					" but it was not expected</li>"
				extra += "</ul>"
			messages.error(request, "Rack scan date stamp: " + str(rack_scanner[0].date_modified) + \
				". Scanned rack does not match with assigned rack wells for this rack!<br><br>" + \
				wrong + missing + extra, extra_tags='safe')
		else:
			if final_check:
				rack.positions_confirmed = True
				rack.save()
			messages.info(request, "Rack scan date stamp: " + str(rack_scanner[0].date_modified) + \
				". Positions confirmed and correct.")
		for rack_scanner_item in rack_scanner:
			rack_scanner_item.acknowledged = True
			rack_scanner_item.save()
	else:
		messages.error(request, "Rack " + rack_id + " not found in Rack scanner CSV. Has the rack been scanned?")

@login_required()
def import_acks(request, test_status=False):
	"""
	Renders import acks page. Allows users to import new GEL1004 acks
	and acknowledge receipt of samples.
	"""
	if request.method == 'POST':
		# import new notifications from the storage location
		if 'import-1004' in request.POST:
			if test_status:
				directory = str(Path.cwd().parent) + '/TestData/Inbound/GEL1004/'
			else:
				directory = LoadConfig().load()['gel1004path']
			for filename in os.listdir(directory):
				if filename.endswith(".csv"):
					datetime_now = datetime.now(pytz.timezone('UTC'))
					path = directory + filename
					with open(path) as csv_file:
						csv_reader = csv.reader(csv_file, delimiter=',')
						line_count=0
						errors = []
						for row in csv_reader:
							if line_count == 0:
								line_count += 1
							else:
								participant_id, error = check_participant_id(row[0].strip())
								if error:
									errors.append(error)
								group_id, error = check_group_id(row[1].strip())
								if error:
									errors.append(error)
								disease_area, error = check_disease_area(row[2].strip())
								if error:
									errors.append(error)
								receiving_rack_id, error = check_rack_id(row[3].strip())
								if error:
									errors.append(error)
								clin_sample_type, error = check_clinical_sample_type(row[4].strip())
								if error:
									errors.append(error)
								glh_sample_consignment_number, error = check_glh_sample_consignment_number(row[5].strip())
								if error:
									errors.append(error)
								laboratory_sample_id, error = check_laboratory_sample_id(row[6].strip())
								if error:
									errors.append(error)
								if Sample.objects.filter(uid=laboratory_sample_id).exists():
									errors.append("A sample with LSID {} already exists in the database".format(laboratory_sample_id))
								laboratory_id, error = check_laboratory_id(row[7].strip())
								if error:
									errors.append(error)
								laboratory_sample_volume, error = check_laboratory_sample_volume(row[8].strip())
								if error:
									errors.append(error)
								receiving_rack_well, error = check_rack_well(row[9].strip())
								if error:
									errors.append(error)
								plating_organisation, error = check_plating_organisation(row[10].strip())
								if error:
									errors.append(error)
								priority, error = check_priority(row[11].strip())
								if error:
									errors.append(error)
								is_proband, error = check_is_proband(row[12].strip())
								if error:
									errors.append(error)
								is_repeat, error = check_is_repeat(row[13].strip())
								if error:
									errors.append(error)
								tissue_type, error = check_tissue_type(row[14].strip())
								if error:
									errors.append(error)
								rack_type, error = check_rack_type(row[15].strip())
								if error:
									errors.append(error)
								if disease_area == 'Rare Disease' and not (rack_type == 'RP' or rack_type == 'RF'):
									errors.append('Rack type does not match sample type for sample {}'.format(str(laboratory_sample_id)))
								if disease_area == 'Cancer' and not (rack_type == 'CG' or rack_type == 'CT'):
									errors.append('Rack type does not match sample type for sample {}'.format(str(laboratory_sample_id)))
						if errors:
							error_message = "Unable to import {} due to the following errors:<ul>".format(filename)
							for error in errors:
								error_message += '<li>' + error
							error_message += '</ul>'
							messages.error(request, error_message, extra_tags='safe')
							break
						else:
							line_count = 0
							csv_file.seek(0)
							for row in csv_reader:
								if line_count == 0:
									line_count += 1
								else:
									participant_id, error = check_participant_id(row[0].strip())
									group_id, error = check_group_id(row[1].strip())
									disease_area, error = check_disease_area(row[2].strip())
									receiving_rack_id, error = check_rack_id(row[3].strip())
									clin_sample_type, error = check_clinical_sample_type(row[4].strip())
									glh_sample_consignment_number, error = check_glh_sample_consignment_number(row[5].strip())
									laboratory_sample_id, error = check_laboratory_sample_id(row[6].strip())
									laboratory_id, error = check_laboratory_id(row[7].strip())
									laboratory_sample_volume, error = check_laboratory_sample_volume(row[8].strip())
									receiving_rack_well, error = check_rack_well(row[9].strip())
									plating_organisation, error = check_plating_organisation(row[10].strip())
									priority, error = check_priority(row[11].strip())
									is_proband, error = check_is_proband(row[12].strip())
									is_repeat, error = check_is_repeat(row[13].strip())
									tissue_type, error = check_tissue_type(row[14].strip())
									rack_type, error = check_rack_type(row[15].strip())
									# gets exiting, or creates new objects
									try:
										gel_1004_csv = Gel1004Csv.objects.get(
											filename = filename,
											plating_organisation=plating_organisation)
									except:
										gel_1004_csv = Gel1004Csv.objects.create(
											filename = filename,
											plating_organisation=plating_organisation,
											report_received_datetime = datetime_now)
									try:
										rack = ReceivingRack.objects.get(
											gel_1004_csv = gel_1004_csv,
											receiving_rack_id = receiving_rack_id,
											laboratory_id = laboratory_id)
									except:
										rack = ReceivingRack.objects.create(
											gel_1004_csv = gel_1004_csv,
											receiving_rack_id = receiving_rack_id,
											laboratory_id = laboratory_id,
											glh_sample_consignment_number = glh_sample_consignment_number)
									# creates new Sample object
									sample = Sample.objects.create(
										uid = laboratory_sample_id,
										receiving_rack = rack,
										participant_id = participant_id,
										group_id = group_id,
										priority = priority,
										disease_area = disease_area,
										clin_sample_type = clin_sample_type,
										laboratory_sample_id = laboratory_sample_id,
										laboratory_sample_volume = laboratory_sample_volume,
										receiving_rack_well = receiving_rack_well,
										is_proband = is_proband,
										is_repeat = is_repeat,
										tissue_type = tissue_type)
									sample = Sample.objects.get(pk=sample.pk)
									if sample.disease_area == 'Rare Disease':
										if sample.is_proband and rack_type == 'RP':
											sample.sample_type = 'Proband'
										elif rack_type == 'RF':
											sample.sample_type = 'Family'
										else:
											raise ValueError('Rack type does not match sample type for sample {}'.format(str(sample)))
									elif sample.disease_area == 'Cancer':
										if 'Normal or Germline sample' in sample.tissue_type and rack_type == 'CG':
											sample.sample_type = 'Cancer Germline'
										elif rack_type == 'CT':
											sample.sample_type = 'Tumour'
										else:
											raise ValueError('Rack type does not match sample type for sample {}'.format(str(sample)))
									sample.save()
									line_count += 1
					os.rename(path, directory + "processed/" + filename)
			return HttpResponseRedirect('/')
		# Generate GEL1005 acks for received samples
		if 	'send-1005' in request.POST:
			pk = request.POST['send-1005']
			gel_1004 = Gel1004Csv.objects.get(pk=pk)
			racks = ReceivingRack.objects.filter(gel_1004_csv=gel_1004)
			if test_status:
				directory = str(Path.cwd().parent) + '/TestData/Outbound/GEL1005/'
			else:
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
							# change primary key to allow sample with same LSID to be sent in future consignment
							sample.uid = sample.uid + '_' + sample.receiving_rack.gel_1004_csv.filename
							sample.save()
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
def acknowledge_samples(request, gel1004, rack, test_status=False):
	rack = ReceivingRack.objects.get(gel_1004_csv=gel1004, receiving_rack_id=rack)
	samples = Sample.objects.filter(receiving_rack=rack)
	sample_select_form = SampleSelectForm()
	log_issue_form = LogIssueForm()
	sample_form_dict = {}
	for sample in samples:
		sample_form_dict[sample] = LogIssueForm(instance=sample)
	if request.method == 'POST':
		if 'rack-scanner' in request.POST:
			confirm_sample_positions(request, rack, samples, first_check=True, test_status=test_status)
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
				sample.issue_outcome = None
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
def problem_samples(request, holding_rack_id=None, test_status=False):
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
	holding_rack = None
	holding_rack_samples = None
	if holding_rack_id:
		holding_rack = HoldingRack.objects.get(holding_rack_id=holding_rack_id, holding_rack_type='Problem', plate__isnull=True)
		holding_rack_samples = Sample.objects.filter(holding_rack_well__holding_rack=holding_rack)
		holding_rack_manager = HoldingRackManager(holding_rack)
		for sample in holding_rack_samples:
			assigned_well_list.append(sample.holding_rack_well.well_id)
			holding_rack_samples_form_dict[sample] = ResolveIssueForm(instance=sample)
	if request.method == 'POST':
		if 'holding' in request.POST:
			sample_select_form = SampleSelectForm()
			holding_rack_form = HoldingRackForm(request.POST)
			if holding_rack_form.is_valid():
				error = False
				holding_rack_id = holding_rack_form.cleaned_data.get('holding_rack_id')
				try:
					receiving_rack = ReceivingRack.objects.get(receiving_rack_id=holding_rack_id)
					if not receiving_rack.is_empty():
						messages.error(request, "You have scanned an active receiving rack. Please scan an exisiting or new Problem rack.")
						error = True
				except:
					pass
				if not error:
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
		if 'rack-scanner' in request.POST:
			holding_rack_form = HoldingRackForm()
			sample_select_form = SampleSelectForm()
			confirm_sample_positions(request, holding_rack, holding_rack_samples)
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
					holding_rack_well = sample.holding_rack_well
					holding_rack_well.sample = None
					holding_rack_well.save()
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
			problem_holding_rack_dict[problem_sample.holding_rack_well.holding_rack].append(problem_sample)
		else:
			problem_holding_rack_dict[problem_sample.holding_rack_well.holding_rack] = [problem_sample]
	return render(request, 'platerplotter/awaiting-holding-rack-assignment.html', {
		"unplated_racks_dict" : unplated_racks_dict,
		"problem_holding_rack_dict" : problem_holding_rack_dict})

@login_required()
def assign_samples_to_holding_rack(request, rack, gel1004=None, holding_rack_id=None):
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
		HoldingRackManager(current_holding_rack).is_half_full()
		HoldingRackManager(current_holding_rack).is_full()
		current_holding_racks_dict[current_holding_rack] = Sample.objects.filter(holding_rack_well__holding_rack=current_holding_rack).count()
	assigned_well_list = []
	holding_rack_samples_form_dict = {}
	holding_rack = None
	holding_rack_samples = None
	problem_samples_in_holding_rack = False
	if holding_rack_id:
		holding_rack = HoldingRack.objects.get(holding_rack_id=holding_rack_id, plate__isnull=True)
		holding_rack_samples = Sample.objects.filter(holding_rack_well__holding_rack=holding_rack)
		holding_rack_manager = HoldingRackManager(holding_rack)
		for sample in holding_rack_samples:
			assigned_well_list.append(sample.holding_rack_well.well_id)
			holding_rack_samples_form_dict[sample] = LogIssueForm(instance=sample)
			if sample.issue_outcome == "Not resolved":
				problem_samples_in_holding_rack = True
	if request.method == 'POST':
		if 'holding' in request.POST:
			sample_select_form = SampleSelectForm()
			holding_rack_form = HoldingRackForm(request.POST)
			if holding_rack_form.is_valid():
				error = False
				holding_rack_id = holding_rack_form.cleaned_data.get('holding_rack_id')
				try:
					receiving_rack = ReceivingRack.objects.get(receiving_rack_id=holding_rack_id)
					if not receiving_rack.is_empty():
						messages.error(request, "You have scanned an active receiving rack. Please scan an exisiting or new Problem rack.")
						error = True
				except:
					pass
				if gel1004:
					if holding_rack_id == rack.receiving_rack_id:
						messages.error(request, "You have scanned the GMC Rack. Please scan the holding rack.")
						error = True
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
					if gel1004:
						url = reverse('assign_samples_to_holding_rack', kwargs={
								'gel1004' : rack.gel_1004_csv.pk,
								'rack' : rack.receiving_rack_id,
								'holding_rack_id' : holding_rack.holding_rack_id,
								})
					else:
						url = reverse('assign_problem_samples_to_holding_rack', kwargs={
								'rack' : problem_holding_rack.holding_rack_id,
								'holding_rack_id' : holding_rack.holding_rack_id,
								})
				else:
					if gel1004:
						url = reverse('assign_samples_to_holding_rack', kwargs={
								'gel1004' : rack.gel_1004_csv.pk,
								'rack' : rack.receiving_rack_id,
								})
					else:
						url = reverse('assign_samples_to_holding_rack', kwargs={
								'rack' : problem_holding_rack.holding_rack_id,
								})
				return HttpResponseRedirect(url)
		if 'rack-scanner' in request.POST:
			holding_rack_form = HoldingRackForm()
			sample_select_form = SampleSelectForm()
			confirm_sample_positions(request, holding_rack, holding_rack_samples)
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
		if 'reopen-rack' in request.POST:
			holding_rack_form = HoldingRackForm()
			sample_select_form = SampleSelectForm()
			pk = request.POST['reopen-rack']
			holding_rack = HoldingRack.objects.get(pk=pk)
			holding_rack.ready_to_plate = False
			holding_rack.save()
			buffer_wells = HoldingRackWell.objects.filter(holding_rack=holding_rack, buffer_added = True)
			for buffer_well in buffer_wells:
				buffer_well.buffer_added = False
				buffer_well.save()
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
						url = reverse('assign_samples_to_holding_rack', kwargs={
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
		"problem_samples_in_holding_rack" : problem_samples_in_holding_rack,
		"holding_rack_samples_form_dict" : holding_rack_samples_form_dict,
		"assigned_well_list" : assigned_well_list,
		"current_holding_racks_dict" : current_holding_racks_dict,
		"holding_rack_rows": holding_rack_rows,
		"holding_rack_columns": holding_rack_columns})

@login_required()
def holding_racks(request, holding_rack_id=None):
	holding_rack_rows = ['A','B','C','D','E','F','G','H']
	holding_rack_columns = ['01','02','03','04','05','06','07','08','09','10','11','12']
	current_holding_racks = HoldingRack.objects.filter(plate__isnull=True).exclude(holding_rack_type='Problem')
	current_holding_racks_dict = {}
	for current_holding_rack in current_holding_racks:
		HoldingRackManager(current_holding_rack).is_half_full()
		HoldingRackManager(current_holding_rack).is_full()
		current_holding_racks_dict[current_holding_rack] = Sample.objects.filter(holding_rack_well__holding_rack=current_holding_rack).count()
	assigned_well_list = []
	holding_rack_samples_form_dict = {}
	holding_rack = None
	holding_rack_samples = None
	problem_samples_in_holding_rack = False
	if holding_rack_id:
		holding_rack = HoldingRack.objects.get(holding_rack_id=holding_rack_id, plate__isnull=True)
		holding_rack_samples = Sample.objects.filter(holding_rack_well__holding_rack=holding_rack)
		holding_rack_manager = HoldingRackManager(holding_rack)
		for sample in holding_rack_samples:
			assigned_well_list.append(sample.holding_rack_well.well_id)
			holding_rack_samples_form_dict[sample] = LogIssueForm(instance=sample)
			if sample.issue_outcome == "Not resolved":
				problem_samples_in_holding_rack = True
	if request.method == 'POST':
		if 'holding' in request.POST:
			holding_rack_form = HoldingRackForm(request.POST)
			if holding_rack_form.is_valid():
				error = False
				holding_rack_id = holding_rack_form.cleaned_data.get('holding_rack_id')
				try:
					receiving_rack = ReceivingRack.objects.get(receiving_rack_id=holding_rack_id)
					if not receiving_rack.is_empty():
						messages.error(request, "You have scanned an active receiving rack. Please scan an exisiting or new Problem rack.")
						error = True
				except:
					pass
				try:
					holding_rack = HoldingRack.objects.get(holding_rack_id=holding_rack_id, plate__isnull=True)
					if holding_rack.holding_rack_type == "Problem":
						messages.error(request, "You have scanned a holding rack being used for Problem samples. Please scan an exisiting Holding rack.")
						error = True
				except:
					messages.error(request, "Holding rack not found with ID: " + holding_rack_id)
					error = True
				if holding_rack and not error:
					url = reverse('holding_racks', kwargs={
							'holding_rack_id' : holding_rack.holding_rack_id,
							})
				else:
					url = reverse('holding_racks')
				return HttpResponseRedirect(url)
		if 'rack-scanner' in request.POST:
			holding_rack_form = HoldingRackForm()
			confirm_sample_positions(request, holding_rack, holding_rack_samples)
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
		if 'reopen-rack' in request.POST:
			holding_rack_form = HoldingRackForm()
			sample_select_form = SampleSelectForm()
			pk = request.POST['reopen-rack']
			holding_rack = HoldingRack.objects.get(pk=pk)
			holding_rack.ready_to_plate = False
			holding_rack.save()
			buffer_wells = HoldingRackWell.objects.filter(holding_rack=holding_rack, buffer_added = True)
			for buffer_well in buffer_wells:
				buffer_well.buffer_added = False
				buffer_well.save()
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
				url = reverse('holding_racks', kwargs={
							'holding_rack_id' : holding_rack.holding_rack_id,
							})
				return HttpResponseRedirect(url)
	else:
		holding_rack_form = HoldingRackForm()
	return render(request, 'platerplotter/holding-racks.html', {
		"holding_rack_form" : holding_rack_form,
		"holding_rack" : holding_rack,
		"holding_rack_samples" : holding_rack_samples,
		"holding_rack_samples_form_dict" : holding_rack_samples_form_dict,
		"problem_samples_in_holding_rack" : problem_samples_in_holding_rack,
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
		HoldingRackManager(rack).is_half_full()
		HoldingRackManager(rack).is_full()
		rack.sample_count = Sample.objects.filter(holding_rack_well__holding_rack=rack).count
	return render(request, 'platerplotter/ready-to-plate.html', {"ready_to_plate" : ready_to_plate})

@login_required()
def plate_holding_rack(request, holding_rack_pk, test_status=False):
	holding_rack = HoldingRack.objects.get(pk=holding_rack_pk)
	samples = Sample.objects.filter(holding_rack_well__holding_rack=holding_rack)
	if request.method == 'POST':
		if "rack-scanner" in request.POST:
			plating_form = PlatingForm()
			confirm_sample_positions(request, holding_rack, samples, final_check = True)
		if "assign-plate" in request.POST:
			plating_form = PlatingForm(request.POST)
			if plating_form.is_valid():
				plate_id = plating_form.cleaned_data.get('plate_id')
				plate = Plate.objects.create(plate_id = plate_id)
				holding_rack.plate = plate
				holding_rack.save()
				# generate output for robot
				holding_rack_wells = HoldingRackWell.objects.filter(holding_rack=holding_rack).order_by('well_id')
				if test_status:
					directory = str(Path.cwd().parent) + '/TestData/Outbound/PlatePlots/'
				else:
					directory = LoadConfig().load()['plate_plots_path']
				filename = holding_rack.holding_rack_id + '.csv'
				path = directory + filename
				with open(path, 'w', newline='') as csvfile:
					writer = csv.writer(csvfile, delimiter=',',
						quotechar=',', quoting=csv.QUOTE_MINIMAL)
					for holding_rack_well in holding_rack_wells:
						well_id = strip_zeros(holding_rack_well.well_id)
						if holding_rack_well.sample or holding_rack_well.buffer_added:
							if holding_rack_well.sample and not holding_rack_well.buffer_added:
								well_contents = holding_rack_well.sample.laboratory_sample_id
							elif holding_rack_well.buffer_added and not holding_rack_well.sample:
								well_contents = "NO READ" # previously read "BUFFER" but Hamilton robot needs reprogramming
							else:
								messages.error(request, 'Well contents invalid. Reported to contain sample and buffer')
						else:
							well_contents = "NO READ"
						writer.writerow([well_id, well_contents, ' 2d_rackid_1', holding_rack.holding_rack_id])
	else:
		plating_form = PlatingForm()
	return render(request, 'platerplotter/plate-holding-rack.html', {
		"holding_rack" : holding_rack,
		"samples" : samples,
		"plating_form" : plating_form})

@login_required()
def ready_to_dispatch(request, test_status=False):
	"""
	Renders page displaying plates that are ready for dispatch
	"""
	ready_to_dispatch = HoldingRack.objects.filter(ready_to_plate=True, plate__isnull=False, plate__gel_1008_csv__isnull=True)
	plate_ids_ready_to_dispatch = []
	plates_ready_to_dispatch = []
	consignment_summaries = {}
	for holding_rack in ready_to_dispatch:
		HoldingRackManager(holding_rack).is_half_full()
		HoldingRackManager(holding_rack).is_full()
		plate_ids_ready_to_dispatch.append(holding_rack.plate.plate_id)
		plates_ready_to_dispatch.append(holding_rack.plate)
		holding_rack.sample_count = Sample.objects.filter(holding_rack_well__holding_rack=holding_rack).count
	if request.method == 'POST':
		if "generate-manifests" in request.POST:
			plate_select_form = PlateSelectForm()
			gel1008_form = Gel1008Form(request.POST)
			selected_plates_list = []
			if gel1008_form.is_valid():
				if request.POST.getlist('selected_plate'):
					plate_pks = request.POST.getlist('selected_plate')
					# determine that all samples that must be sent in the same consignment have been selected
					all_cancer_samples = set()
					all_rare_disease_samples = set()
					for pk in plate_pks:
						plate = Plate.objects.get(pk=pk)
						if plate.holding_rack.holding_rack_type == "Cancer Germline" or plate.holding_rack.holding_rack_type == "Tumour":
							samples = Sample.objects.filter(holding_rack_well__holding_rack__plate = plate)
							for sample in samples:
								all_cancer_samples.add(sample)
						if plate.holding_rack.holding_rack_type == "Proband" or plate.holding_rack.holding_rack_type == "Family":
							samples = Sample.objects.filter(holding_rack_well__holding_rack__plate = plate)
							for sample in samples:
								all_rare_disease_samples.add(sample)
					matching_cancer_samples_not_selected = set()
					for sample in all_cancer_samples:
						matching_samples = Sample.objects.filter(participant_id = sample.participant_id,
							sample_received = True,
							disease_area = 'Cancer',
							holding_rack_well__holding_rack__plate__gel_1008_csv__isnull = True).exclude(
							issue_outcome="Sample returned to extracting GLH").exclude(
							issue_outcome="Sample destroyed")
						for matching_sample in matching_samples:
							if matching_sample not in all_cancer_samples:
								matching_cancer_samples_not_selected.add(matching_sample)
					if matching_cancer_samples_not_selected:
						cancer_sample_info = '<ul>'
						for sample in matching_cancer_samples_not_selected:
							if hasattr(sample, 'holding_rack_well'):
								if sample.holding_rack_well.holding_rack.plate:
									cancer_sample_info += "<li> " + sample.laboratory_sample_id + " in plate " + \
										sample.holding_rack_well.holding_rack.plate.plate_id + " in well " + \
										sample.holding_rack_well.well_id + '</li>'
								else:
									cancer_sample_info += "<li> " + sample.laboratory_sample_id + " in holding rack " + \
										sample.holding_rack_well.holding_rack.holding_rack_id + " in well " + \
										sample.holding_rack_well.well_id + '</li>'
							else:
								cancer_sample_info += "<li> " + sample.laboratory_sample_id + " in GMC rack " + \
									sample.receiving_rack.receiving_rack_id + " in well " + \
									sample.receiving_rack_well + '</li>'
						cancer_sample_info += ' </ul>'
						messages.error(request, "All synchronous multi-tumour samples must be sent in the same consignment. " + 
								"The following samples need to be sent in the same consignment as the plates you have selected:<br>" +
								cancer_sample_info, extra_tags='safe')
					matching_rare_disease_samples_not_selected = set()
					for sample in all_rare_disease_samples:
						matching_samples = Sample.objects.filter(group_id = sample.group_id,
							sample_received = True,
							disease_area = 'Rare Disease',
							holding_rack_well__holding_rack__plate__gel_1008_csv__isnull = True).exclude(
							issue_outcome="Sample returned to extracting GLH").exclude(
							issue_outcome="Sample destroyed")
						for matching_sample in matching_samples:
							if matching_sample not in all_rare_disease_samples:
								matching_rare_disease_samples_not_selected.add(matching_sample)
					if matching_rare_disease_samples_not_selected:
						rare_disease_sample_info = '<ul>'
						for sample in matching_rare_disease_samples_not_selected:
							if hasattr(sample, 'holding_rack_well'):
								if sample.holding_rack_well.holding_rack.plate:
									rare_disease_sample_info += "<li> " + sample.laboratory_sample_id + " in plate " + \
										sample.holding_rack_well.holding_rack.plate.plate_id + " in well " + \
										sample.holding_rack_well.well_id + '</li>'
								else:
									rare_disease_sample_info += "<li> " + sample.laboratory_sample_id + " in holding rack " + \
										sample.holding_rack_well.holding_rack.holding_rack_id + " in well " + \
										sample.holding_rack_well.well_id + '</li>'
							else:
								rare_disease_sample_info += "<li> " + sample.laboratory_sample_id + " in GMC rack " + \
									sample.receiving_rack.receiving_rack_id + " in well " + \
									sample.receiving_rack_well + '</li>'
						rare_disease_sample_info += ' </ul>'
						messages.error(request, "All family member samples must be sent in the same consignment as the proband. " + 
								"The following samples need to be sent in the same consignment as the plates you have selected:<br>" +
								rare_disease_sample_info, extra_tags='safe')
					if not matching_rare_disease_samples_not_selected and not matching_cancer_samples_not_selected:
						consignment_number = gel1008_form.cleaned_data.get('consignment_number')
						date_of_dispatch = gel1008_form.cleaned_data.get('date_of_dispatch')
						matching_gel_1008s = Gel1008Csv.objects.filter(consignment_number=consignment_number)
						error = False
						warning = False
						for matching_gel_1008 in matching_gel_1008s:
							if matching_gel_1008.message_generated:
								warning = True
							if matching_gel_1008.date_of_dispatch != date_of_dispatch and not matching_gel_1008.message_generated:
								error = True
						if warning:
							messages.warning(request, "Warning, this consignment number has been used before.")
						if error:
							messages.error(request, "There is an open consignment with this number but the date of dispatch did not match.")
						else:
							if test_status:
								manifest_directory = str(Path.cwd().parent) + '/TestData/Outbound/ConsignmentManifests/'
							else:
								manifest_directory = LoadConfig().load()['consignment_manifest_path']
							for pk in plate_pks:
								datetime_now = datetime.now(pytz.timezone('UTC'))
								filename = "ngis_bio_to_gel_sample_dispatch_" + datetime.now(pytz.timezone('UTC')).strftime("%Y%m%d_%H%M%S") + ".csv"
								# need to wait 1 second to make sure filenames for GEL1008s are different
								time.sleep(1)
								gel_1008_csv = Gel1008Csv.objects.create(
									filename = filename,
									report_generated_datetime = datetime_now,
									consignment_number = consignment_number,
									date_of_dispatch = date_of_dispatch)
								plate = Plate.objects.get(pk=pk)
								plate.gel_1008_csv = gel_1008_csv
								plate.save()
								filename = consignment_number + '_' + plate.plate_id + '.pdf'
								manifest_path = manifest_directory + filename
								doc = SimpleDocTemplate(manifest_path)
								doc.pagesize = landscape(A4)
								elements = []
								data = [['Plate ID', 'Plate Consignment Number', 'Plate Date of Dispatch', 'Type of case',
										 'Well ID', 'Well Type', 'Participant ID', 'Laboratory Sample ID']]
								plate_type = plate.holding_rack.holding_rack_type
								if plate_type == 'Proband':
									type_of_case = 'RP'
								elif plate_type == 'Family':
									type_of_case = 'RF'
								elif plate_type == 'Cancer Germline':
									type_of_case = 'CG'
								elif plate_type == 'Tumour':
									type_of_case = 'CT'
								if test_status:
									gel1008_directory = str(Path.cwd().parent) + '/TestData/Outbound/GEL1008/'
								else:
									if type_of_case == 'RP' or type_of_case == 'CG':
										gel1008_directory = LoadConfig().load()['gel1008path'] + 'RP-CG/'
									else:
										gel1008_directory = LoadConfig().load()['gel1008path'] + 'RF-CT/'
								filename = "ngis_bio_to_gel_sample_dispatch_" + type_of_case + "_" + datetime.now(pytz.timezone('UTC')).strftime("%Y%m%d_%H%M%S") + ".csv"
								gel1008_path = gel1008_directory + filename
								with open(gel1008_path, 'w', newline='') as csvfile:
									writer = csv.writer(csvfile, delimiter=',',
										quotechar=',', quoting=csv.QUOTE_MINIMAL)
									writer.writerow(['Plate ID', 'Plate Consignment Number', 'Plate Date of Dispatch',
										'type_of_case', 'Well ID', 'Well Type', 'Participant ID', 'Laboratory Sample ID',
										'Normalised Biorepository Sample Volume', 'Normalised Biorepository Concentration'])
									holding_rack_wells = HoldingRackWell.objects.filter(holding_rack=plate.holding_rack).order_by('well_id')
									for holding_rack_well in holding_rack_wells:
										if holding_rack_well.sample or holding_rack_well.buffer_added:
											plate_id = plate.plate_id
											plate_consignment_number = gel_1008_csv.consignment_number
											plate_date_of_dispatch = gel_1008_csv.date_of_dispatch.replace(microsecond=0).isoformat().replace('+00:00', 'Z')
											well_id = holding_rack_well.well_id
											if holding_rack_well.sample and not holding_rack_well.buffer_added:
												well_type = "Sample"
												participant_id = holding_rack_well.sample.participant_id
												laboratory_sample_id = holding_rack_well.sample.laboratory_sample_id
												norm_biorep_sample_vol = holding_rack_well.sample.norm_biorep_sample_vol
												norm_biorep_conc = holding_rack_well.sample.norm_biorep_conc
											elif holding_rack_well.buffer_added and not holding_rack_well.sample:
												well_type = "Buffer"
												participant_id = ""
												laboratory_sample_id = ""
												norm_biorep_sample_vol = ""
												norm_biorep_conc = ""
											else:
												messages.error(request, 'Well contents invalid. Reported to contain sample and buffer')
											writer.writerow([plate_id, plate_consignment_number, plate_date_of_dispatch, type_of_case, well_id, 
												well_type, participant_id, laboratory_sample_id, norm_biorep_sample_vol, norm_biorep_conc])
											data.append([plate_id, plate_consignment_number, plate_date_of_dispatch, type_of_case,
												well_id, well_type, participant_id, laboratory_sample_id])
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
									consignment_summaries[filename] = manifest_path
							manifests = '<ul>'
							for manifest, path in consignment_summaries.items():
								manifests += '<li><a href="/download/' + manifest + '" target="_blank">' + manifest + '</a></li>'
							manifests += '</ul>'
							messages.info(request, "GEL1008 messages have been generated for the following consignment manifests, click to download:<br>" +
								manifests, extra_tags='safe')
				else:
					messages.warning(request, "No plates selected!")
				return HttpResponseRedirect('/ready-to-dispatch/')
		if "plate" in request.POST:
			gel1008_form = Gel1008Form()
			plate_select_form = PlateSelectForm(request.POST)
			selected_plates = request.POST['selected_plates']
			selected_plates_list = selected_plates.split(',')
			for selected_plate in selected_plates_list:
				if selected_plate == "":
					selected_plates_list.remove(selected_plate)
			selected_plates_list = list(map(int, selected_plates_list))
			if plate_select_form.is_valid():
				plate_id = plate_select_form.cleaned_data.get('plate_id')
				if plate_id in plate_ids_ready_to_dispatch:
					for plate_ready_to_dispatch in plates_ready_to_dispatch:
						if plate_ready_to_dispatch.plate_id == plate_id:
							if plate_ready_to_dispatch.pk in selected_plates_list:
								messages.warning(request, plate_id + " already selected for this consignment.")
							else:
								selected_plates_list.append(plate_ready_to_dispatch.pk)
								messages.info(request, plate_id + " added to the consignment list.")
				else:
					messages.error(request, plate_id + " not found in list of plates ready for dispatch.")
	else:
		selected_plates_list = []
		plate_select_form = PlateSelectForm()
		gel1008_form = Gel1008Form()
	return render(request, 'platerplotter/ready-to-dispatch.html', {
		"ready_to_dispatch" : ready_to_dispatch,
		"gel1008_form" : gel1008_form,
		"plate_select_form" : plate_select_form,
		"selected_plates_list" : selected_plates_list})

@login_required()
def consignments_for_collection(request, test_status=False):
	consignments = Gel1008Csv.objects.filter(consignment_collected=False)
	consignment_no_dict = {}
	for gel_1008 in consignments:
		if gel_1008.consignment_number in consignment_no_dict:
			consignment_no_dict[gel_1008.consignment_number].append(Plate.objects.get(gel_1008_csv=gel_1008))
		else:
			consignment_no_dict[gel_1008.consignment_number] = [Plate.objects.get(gel_1008_csv=gel_1008)] 
	for consignment, plates in consignment_no_dict.items():
		for plate in plates:
			plate.sample_count = Sample.objects.filter(holding_rack_well__holding_rack__plate=plate).count()
			HoldingRackManager(plate.holding_rack).is_half_full()
			HoldingRackManager(plate.holding_rack).is_full()
	if request.method == 'POST':
		if "send-consignment" in request.POST:
			consignment = request.POST['send-consignment']
			plates = consignment_no_dict[consignment]
			for plate in plates:
				plate.gel_1008_csv.consignment_collected = True
				plate.gel_1008_csv.save()
			messages.info(request, "Consignment collected.")
		return HttpResponseRedirect('/consignments-for-collection/')
	return render(request, 'platerplotter/consignments-for-collection.html', {
		"consignment_no_dict" : consignment_no_dict
		})

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

def login_user(request):
	"""Log user in using Django's authentication system; if successful, redirect to home page.
	:param request:
	:return:
	"""
	# filters out Internet Explorer users
	if "MSIE" in request.META['HTTP_USER_AGENT']:
		return render(request, 'platerplotter/incompatible-browser.html')
	else:
		errors = []

		if request.method == 'POST':
			username = request.POST['username'].upper()
			request.session['user'] = username
			password = request.POST['password']
			request.session['password'] = password
			user = authenticate(
				username=username,
				password=password
			)

			if user:
				if user.is_active:
					login(request, user)
					return HttpResponseRedirect('/')
				else:
					errors.append('Failed to login: account inactive.')
			else:
				errors.append('Failed to login: invalid login details.')

		return render(
			request,
			'registration/login.html',
			{
				'errors': errors
			}
		)

def register(request):
	created = False
	matching_users = []
	if request.method == 'POST':
		email = request.POST['email']
		username = request.POST['username'].upper()
		password = request.POST['password']
		matching_users = User.objects.filter(username=username)
		if not matching_users:
			u = User.objects.create_user(username, email, password)
			u.is_active = False
			u.save()
			created = True
	return render(request, 'registration/register.html', {'created': created, 'matching_users': matching_users})

def logout_user(request):
	"""Log user out using Django's authentication system, and redirect to login page.
	:param request:
	:return:
	"""
	logout(request)
	return HttpResponseRedirect('/')


def download_manifest(request, filename):
	directory = LoadConfig().load()['consignment_manifest_path']
	with open(directory + filename, 'rb') as fh:
		response = HttpResponse(fh.read(), content_type="application/pdf")
		response['Content-Disposition'] = 'inline; filename=' + os.path.basename('output/' + filename)
		return response