from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.urls import reverse
from platerplotter.models import Gel1004Csv, Gel1005Csv, Gel1008Csv, Rack, Plate, Sample, RackScanner, RackScannerSample
from platerplotter.config.load_config import LoadConfig
from platerplotter.forms import HoldingRackForm, SampleSelectForm, PlatingForm, Gel1008Form, ParticipantIdForm
from datetime import datetime
from django.core.exceptions import ValidationError
from platerplotter.plate_manager import PlateManager
import csv, os
import pytz


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

def remove_padded_zeros(position):
	letter = position[0]
	number = position[1:]
	if number[0] == '0':
		number = number[1]
	return letter + number


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
					datetime_now = datetime.now(pytz.timezone('Europe/London'))
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
										plating_organisation=row[10])
								except:
									gel_1004_csv = Gel1004Csv.objects.create(
										filename = filename,
										plating_organisation=row[10],
										report_received_datetime = datetime_now)
								try:
									rack = Rack.objects.get(
										gmc_rack_id = row[3],
										laboratory_id = row[7])
								except:
									rack = Rack.objects.create(
										gel_1004_csv = gel_1004_csv,
										gmc_rack_id = row[3],
										laboratory_id = row[7])
								# creates new Sample object
								# need to add regex error checking to input
								sample = Sample.objects.create(
									rack = rack,
									participant_id = row[0],
									group_id = row[1],
									priority = row[11],
									disease_area = row[2],
									clin_sample_type = row[4],
									glh_sample_consignment_number = row[5],
									laboratory_sample_id = row[6],
									laboratory_sample_volume = row[8],
									gmc_rack_well = remove_padded_zeros(row[9]),
									is_proband=row[12])
								sample = Sample.objects.get(pk=sample.pk)
								if sample.disease_area == 'Rare Disease':
									if sample.is_proband:
										sample.sample_type = 'Proband'
									else:
										sample.sample_type = 'Parent'
								elif sample.disease_area == 'Solid Tumour':
									if 'tumour' in sample.clin_sample_type:
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
			datetime_now = datetime.now(pytz.timezone('Europe/London'))
			filename = "ngis_bio_to_gel_samples_received_" + datetime.now(pytz.timezone('Europe/London')).strftime("%y%m%d_%H%M%S") + ".csv"
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
						writer.writerow([sample.participant_id, rack.laboratory_id,
							sample.sample_received, sample.sample_received_datetime,
							gel_1005.report_generated_datetime, sample.laboratory_sample_id])
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

def acknowledge_samples(request, rack):
	rack = Rack.objects.get(gmc_rack_id=rack)
	samples = Sample.objects.filter(rack=rack)
	sample_select_form = SampleSelectForm()
	if request.method == 'POST':
		if 'rack-scanner' in request.POST:
			directory = LoadConfig().load()['rack_scanner_received_path']
			for filename in os.listdir(directory):
				if filename.endswith(".csv"):
					path = directory + filename
					date_modified = datetime.fromtimestamp(os.path.getmtime(path))
					with open(path, 'r') as csvFile:
						reader = csv.reader(csvFile, delimiter=',', skipinitialspace=True)
						for row in reader:
							if row[1] != 'NO READ':
								rack_scanner, created = RackScanner.objects.get_or_create(
									filename=filename,
									scanned_id=row[3],
									date_modified=date_modified,
									workflow_position='received_rack')
								RackScannerSample.objects.get_or_create(rack_scanner=rack_scanner,
									sample_id=row[1],
									position=row[0])
					os.rename(path, directory + "processed/" + filename)
			rack_scanner = RackScanner.objects.filter(scanned_id=rack.gmc_rack_id,
				workflow_position='received_rack',
				acknowledged=False)
			if rack_scanner:
				rack_scanner_samples = RackScannerSample.objects.filter(rack_scanner=rack_scanner[0])
				samples_received_wrong_position = []
				extra_samples = []
				for sample in samples:
					for rack_scanner_sample in rack_scanner_samples:
						if sample.laboratory_sample_id == rack_scanner_sample.sample_id:
							if sample.gmc_rack_well == rack_scanner_sample.position:
								sample.sample_received = True
								sample.sample_received_datetime = datetime.now(pytz.timezone('Europe/London'))
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
					sample.sample_received_datetime = datetime.now(pytz.timezone('Europe/London'))
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
				sample.sample_received_datetime = datetime.now(pytz.timezone('Europe/London'))
			sample.save()
			url = reverse('acknowledge_samples', kwargs={
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

def plate_samples(request, rack, plate_id=None):
	plate_rows = ['A','B','C','D','E','F','G','H']
	plate_columns = ['1','2','3','4','5','6','7','8','9','10','11','12']
	rack = Rack.objects.get(gmc_rack_id=rack)
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
		plate = Plate.objects.get(holding_rack_id=plate_id)
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
							'rack' : rack.gmc_rack_id,
							'plate_id' : plate.holding_rack_id,
							})
				else:
					url = reverse('plate_samples', kwargs={
							'rack' : rack.gmc_rack_id,
							})
				return HttpResponseRedirect(url)
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
			directory = LoadConfig().load()['rack_scanner_plated_path']
			for filename in os.listdir(directory):
				if filename.endswith(".csv"):
					path = directory + filename
					date_modified = datetime.fromtimestamp(os.path.getmtime(path))
					with open(path, 'r') as csvFile:
						reader = csv.reader(csvFile, delimiter=',', skipinitialspace=True)
						for row in reader:
							if row[1] != 'NO READ':
								rack_scanner, created = RackScanner.objects.get_or_create(
									filename=filename,
									scanned_id=row[3],
									date_modified=date_modified,
									workflow_position='plated_rack')
								RackScannerSample.objects.get_or_create(rack_scanner=rack_scanner,
									sample_id=row[1],
									position=row[0])
					os.rename(path, directory + "processed/" + filename)
			rack_scanner = RackScanner.objects.filter(scanned_id=plate.holding_rack_id,
				workflow_position='plated_rack',
				acknowledged=False)
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
				datetime_now = datetime.now(pytz.timezone('Europe/London'))
				filename = "ngis_bio_to_gel_sample_dispatch_" + datetime.now(pytz.timezone('Europe/London')).strftime("%y%m%d_%H%M%S") + ".csv"
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
								sample.plate_well_id, gel_1008_csv.consignment_number, gel_1008_csv.date_of_dispatch])
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