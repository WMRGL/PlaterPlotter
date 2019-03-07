from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.urls import reverse
from platerplotter.models import Gel1004Csv, Gel1005Csv, Gel1008Csv, Rack, Plate, Sample
from platerplotter.config.load_config import LoadConfig
from platerplotter.forms import HoldingRackForm, SampleSelectForm, PlatingForm, Gel1008Form #ReceivedSampleForm
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
									gmc_rack_well = row[9],
									is_proband=row[12])
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
	if request.method == 'POST':
		if 'rack-acked' in request.POST:
			rack.rack_acknowledged = True
			rack.save()
			return HttpResponseRedirect('/')
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
	return render(request, 'acknowledge-samples.html', {"rack" : rack,
		"samples" : samples})

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
	rack = Rack.objects.get(gmc_rack_id=rack)
	samples = Sample.objects.filter(rack=rack,
		plate__isnull = True,
		rack__gel_1004_csv__gel_1005_csv__isnull = False,
		sample_received = True)
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
					messages.info(request, "You have scanned the GMC Rack. Please scan the holding rack.")
				else:
					try:
						plate = Plate.objects.get(holding_rack_id=holding_rack_id)
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
			print(request.POST['ready'])
			pk = request.POST['ready']
			plate = Plate.objects.get(pk=pk)
			print(plate)
			print(plate.holding_rack_id)
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
					plate_manager.assign_well(sample)
					messages.info(request, lab_sample_id + " assigned to well " + sample.plate_well_id)
				else:
					messages.info(request, lab_sample_id + " not found in GLH Rack " + rack.gmc_rack_id)
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
		"assigned_well_list" : assigned_well_list})

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
				messages.info(request, "No plates selected!")
			return HttpResponseRedirect('/ready-to-dispatch/')
	else:
		gel1008_form = Gel1008Form()
	return render(request, 'ready-to-dispatch.html', {
		"ready_to_dispatch" : ready_to_dispatch,
		"gel1008_form" : gel1008_form})