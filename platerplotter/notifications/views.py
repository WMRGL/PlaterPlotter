import os
import re

import pytz
import csv
from datetime import datetime
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from platerplotter.config.load_config import LoadConfig
from platerplotter.models import Sample, Gel1005Csv, Gel1004Csv, ReceivingRack
from problemsamples.forms import SampleSelectForm, LogIssueForm
from problemsamples.views import confirm_sample_positions


# Create your views here.

def check_participant_id(participant_id):
	error = None
	if not re.match(r'^p\d{11}$', participant_id.lower()):
		error = 'Incorrect participant ID. Received {} which does not match the required specification.'.format(
			participant_id)
	return participant_id.lower(), error


def check_group_id(group_id):
	error = None
	if not re.match(r'^r\d{11}$', group_id.lower()):
		error = 'Incorrect group ID. Received {} which does not match the required specification.'.format(group_id)
	return group_id.lower(), error


def check_disease_area(disease_area):
	error = None
	accepted_values = ['Cancer', 'Rare Disease']
	if disease_area.title() not in accepted_values:
		error = 'Incorrect disease area. Received {}. Must be either cancer or rare disease.'.format(disease_area)
	return disease_area.title(), error


def check_rack_id(rack_id):
	error = None
	if 8 > len(rack_id) or len(rack_id) > 12:
		error = 'Incorrect rack ID. Received {} which does not match the required specification.'.format(rack_id)
	return rack_id.upper(), error


def check_clinical_sample_type(clin_sample_type):
	error = None
	return clin_sample_type.lower(), error


def check_glh_sample_consignment_number(glh_sample_consignment_number):
	error = None
	if not re.match(r'^[a-z]{3}-\d{4}-\d{2}-\d{2}-\d{2}-[1,2]$',
					glh_sample_consignment_number.lower()) and not re.match(
		r'^[a-z]{3}-\d{4}-\d{2}-\d{2}-[1,2]$', glh_sample_consignment_number.lower()) and not re.match(
		r'^.*$', glh_sample_consignment_number.lower()):
		error = 'Incorrect GLH sample consignment number. Received {} which does not match the required specification.'.format(
			glh_sample_consignment_number)
	return glh_sample_consignment_number.lower(), error


def check_laboratory_sample_id(laboratory_sample_id):
	error = None
	if not re.match(r'^\d{10}$', laboratory_sample_id):
		error = 'Incorrect laboratory sample ID. Received {}. Should be 10 digits'.format(laboratory_sample_id)
	return laboratory_sample_id, error


def check_laboratory_id(laboratory_id):
	error = None
	accepted_ids = ["yne", "now", "eme", "lnn", "lns", "wwm", "sow"]
	if laboratory_id.lower() not in accepted_ids:
		error = 'Incorrect laboratory ID. Received {} which is not on the list of accepted laboratory IDs.'.format(
			laboratory_id)
	return laboratory_id.lower(), error


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


def check_plating_organisation(plating_organisation):
	error = None
	if plating_organisation.lower() != 'wwm':
		error = 'Plating organisation entered as {}. Expected "wmm".'.format(plating_organisation.lower())
	return plating_organisation.lower(), error


def check_priority(priority):
	error = None
	accepted_values = ['Urgent', 'Routine']
	if priority.title() not in accepted_values:
		error = 'Incorrect priority. Received {}. Must be either routine or urgent.'.format(priority)
	return priority.title(), error


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


def check_sample_delivery_mode(sample_delivery_mode):
	error = None
	accepted_values = ["Tumour First", "Germline Late", "Family Only", "Standard"]
	if sample_delivery_mode.title() not in accepted_values:
		error = 'Incorrect sample_delivery_mode. Received {} which is not in the list of accepted values'.format(sample_delivery_mode)
	return sample_delivery_mode.title(), error

def post_volume_check(request):
	if request.accepts("/post/ajax/volume"):
		gel_1004_id = request.GET.get('gel1004_id')
		rack_id = request.GET.get('rack_id')
		receiving_rack = ReceivingRack.objects.get(id=rack_id)
		all_receiving_racks = ReceivingRack.objects.filter(gel_1004_csv=gel_1004_id)
		# toggle between checked and not checked each time button is pressed
		if receiving_rack.volume_checked:
			receiving_rack.volume_checked = False
		else:
			receiving_rack.volume_checked = True
		receiving_rack.save()
		all_checked = True
		all_racks_acked = True
		for rack in all_receiving_racks:
			if not rack.volume_checked:
				all_checked = False
			if not rack.rack_acknowledged:
				all_racks_acked = False
		data = {}
		data[rack_id] = receiving_rack.volume_checked
		data['all_checked'] = all_checked
		data['all_acked'] = all_racks_acked
		return JsonResponse(data)


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
						line_count = 0
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
								glh_sample_consignment_number, error = check_glh_sample_consignment_number(
									row[5].strip())
								if error:
									errors.append(error)
								laboratory_sample_id, error = check_laboratory_sample_id(row[6].strip())
								if error:
									errors.append(error)
								if Sample.objects.filter(uid=laboratory_sample_id).exists():
									errors.append("A sample with LSID {} already exists in the database".format(
										laboratory_sample_id))
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
								# Try sample_delivery_mode allows us to avoid errors caused if the old Gel1004 message is sent.
								try:
									sample_delivery_mode, error = check_sample_delivery_mode(row[16].strip())
									if error:
										errors.append(error)
								except IndexError:
									# allows old gel1004 messages without a sample_delivery_mode pass.
									pass
								if disease_area == 'Rare Disease' and not (rack_type == 'RP' or rack_type == 'RF'):
									errors.append('Rack type does not match sample type for sample {}'.format(
										str(laboratory_sample_id)))
								if disease_area == 'Cancer' and not (rack_type == 'CG' or rack_type == 'CT'):
									errors.append('Rack type does not match sample type for sample {}'.format(
										str(laboratory_sample_id)))
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
									glh_sample_consignment_number, error = check_glh_sample_consignment_number(
										row[5].strip())
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
									# Try sample_delivery_mode allows us to avoid errors caused if the old Gel1004 message is sent.
									# And assign "Standard" to samples from old Gel1004 message
									try:
										sample_delivery_mode, error = check_sample_delivery_mode(row[16].strip())
									except IndexError:
										sample_delivery_mode = "Standard"
									# gets exiting, or creates new objects
									try:
										gel_1004_csv = Gel1004Csv.objects.get(
											filename=filename,
											plating_organisation=plating_organisation)
									except:
										gel_1004_csv = Gel1004Csv.objects.create(
											filename=filename,
											plating_organisation=plating_organisation,
											report_received_datetime=datetime_now)
									try:
										rack = ReceivingRack.objects.get(
											gel_1004_csv=gel_1004_csv,
											receiving_rack_id=receiving_rack_id,
											laboratory_id=laboratory_id)
									except:
										if rack_type == 'RP':
											rt = 'Proband'
										elif rack_type == 'RF':
											rt = 'Family'
										elif rack_type == 'CG':
											rt = 'Cancer Germline'
										elif rack_type == 'CT':
											rt = 'Tumour'
										else:
											rt = None
										rack = ReceivingRack.objects.create(
											gel_1004_csv=gel_1004_csv,
											receiving_rack_id=receiving_rack_id,
											laboratory_id=laboratory_id,
											disease_area=disease_area,
											rack_type=rt,
											glh_sample_consignment_number=glh_sample_consignment_number)
									# creates new Sample object
									sample = Sample.objects.create(
										uid=laboratory_sample_id,
										receiving_rack=rack,
										participant_id=participant_id,
										group_id=group_id,
										priority=priority,
										disease_area=disease_area,
										clin_sample_type=clin_sample_type,
										laboratory_sample_id=laboratory_sample_id,
										laboratory_sample_volume=laboratory_sample_volume,
										receiving_rack_well=receiving_rack_well,
										is_proband=is_proband,
										is_repeat=is_repeat,
										tissue_type=tissue_type,
										sample_delivery_mode=sample_delivery_mode)

									sample = Sample.objects.get(pk=sample.pk)
									if sample.disease_area == 'Rare Disease':
										if sample.is_proband and rack_type == 'RP':
											sample.sample_type = 'Proband'
										elif rack_type == 'RF':
											sample.sample_type = 'Family'
										else:
											raise ValueError(
												'Rack type does not match sample type for sample {}'.format(
													str(sample)))
									elif sample.disease_area == 'Cancer':
										if 'Normal or Germline sample' in sample.tissue_type and rack_type == 'CG':
											sample.sample_type = 'Cancer Germline'
										elif rack_type == 'CT':
											sample.sample_type = 'Tumour'
										else:
											raise ValueError(
												'Rack type does not match sample type for sample {}'.format(
													str(sample)))
									sample.save()
									line_count += 1
					os.rename(path, directory + "processed/" + filename)
			return HttpResponseRedirect('/')
		# Generate GEL1005 acks for received samples
		if 'send-1005' in request.POST:
			pk = request.POST['send-1005']
			gel_1004 = Gel1004Csv.objects.get(pk=pk)
			racks = ReceivingRack.objects.filter(gel_1004_csv=gel_1004)
			if test_status:
				directory = str(Path.cwd().parent) + '/TestData/Outbound/GEL1005/'
			else:
				directory = LoadConfig().load()['gel1005path']
			datetime_now = datetime.now(pytz.timezone('UTC'))
			filename = "ngis_bio_to_gel_samples_received_" + datetime.now(pytz.timezone('UTC')).strftime(
				"%Y%m%d_%H%M%S") + ".csv"
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
							received_datetime = sample.sample_received_datetime.replace(
								microsecond=0).isoformat().replace('+00:00', 'Z')
						writer.writerow([sample.participant_id, rack.laboratory_id,
										 sample_received, received_datetime,
										 gel_1005.report_generated_datetime.replace(microsecond=0).isoformat().replace(
											 '+00:00', 'Z'), sample.laboratory_sample_id])
			return HttpResponseRedirect('/')
	unacked_gel_1004 = Gel1004Csv.objects.filter(gel_1005_csv__isnull=True)
	unacked_racks_dict = {}
	for gel_1004 in unacked_gel_1004:
		unacked_racks_dict[gel_1004] = ReceivingRack.objects.filter(gel_1004_csv=gel_1004)
		for gel_1004, racks in unacked_racks_dict.items():
			all_racks_acked = True
			all_racks_volume_checked = True
			for rack in racks:
				rack.no_samples = Sample.objects.filter(receiving_rack=rack).count()
				if not rack.rack_acknowledged:
					all_racks_acked = False
				if not rack.volume_checked:
					all_racks_volume_checked = False
			gel_1004.all_racks_acked = all_racks_acked
			gel_1004.all_racks_volume_checked = all_racks_volume_checked
	return render(request, 'notifications/import-acks.html', {
		"unacked_racks_dict": unacked_racks_dict,
	})


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
			url = reverse('notifications:acknowledge_samples', kwargs={
				"gel1004": gel1004,
				"rack": rack.receiving_rack_id,
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
				url = reverse('notifications:acknowledge_samples', kwargs={
					"gel1004": gel1004,
					"rack": rack.receiving_rack_id,
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
				url = reverse('notifications:acknowledge_samples', kwargs={
					"gel1004": gel1004,
					"rack": rack.receiving_rack_id,
				})
				return HttpResponseRedirect(url)
	all_samples_received = True
	for sample in samples:
		if not sample.sample_received:
			all_samples_received = False
	if all_samples_received:
		messages.info(request, "All samples received")

	if 'mark-as-problem-rack' in request.POST:
		selected_rack = Sample.objects.filter(receiving_rack=rack.pk)
		url = reverse('notifications:acknowledge_samples', kwargs={
			"gel1004": gel1004,
			"rack": rack.receiving_rack_id,
		})
		for sample in selected_rack:
			if not sample.sample_received:
				messages.error(request, "Kindly mark sample as received")
				return HttpResponseRedirect(url)

			sample.comment = request.POST['comment']
			sample.issue_identified = True
			sample.issue_outcome = "Not resolved"
			sample.save()

		return HttpResponseRedirect(url)

	return render(request, 'notifications/acknowledge-samples.html', {"rack": rack,
																	  "samples": samples,
																	  "sample_select_form": sample_select_form,
																	  "sample_form_dict": sample_form_dict,
																	  "log_issue_form": log_issue_form,
																	  "all_samples_received": all_samples_received})
