from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.urls import reverse
from platerplotter.models import Gel1004Csv, Gel1005Csv, Gel1008Csv, Rack, Plate, Sample
from platerplotter.config.load_config import LoadConfig
#from platerplotter.forms import ReceivedSampleForm
from datetime import datetime
import csv, os
import pytz

def ajax_change_sample_received_status(request):
    sample_received = request.GET.get('sample_received', False)
    sample_id = request.GET.get('sample_id', False)
    # first you get your Job model
    sample = Sample.objects.get(pk=sample_id)
    try:
        sample.sample_received = sample_received
        sample.save()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False})
    return JsonResponse(data)

def import_acks(request):
	"""
	Renders index page.
	"""
	if request.method == 'POST':
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
			unacked_gel_1004 = Gel1004Csv.objects.filter(gel_1005_csv__isnull = True)
			unacked_racks_dict = {}
			for gel_1004 in unacked_gel_1004:
				unacked_racks_dict[gel_1004] = Rack.objects.filter(gel_1004_csv=gel_1004)
			return render(request, 'import-acks.html', {"unacked_racks_dict" : unacked_racks_dict})
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
			print(filename)
			#gel1004_with_matched_samples = Gel1004csv.objects.filter(receivedSample__isnull = False, gel1005__isnull = True)
			#print(len(gel1004_with_matched_samples))
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
			url = reverse('acknowledge-samples', kwargs={
				"rack" : rack.gmc_rack_id,
				})
			return HttpResponseRedirect(url)
	return render(request, 'acknowledge-samples.html', {"rack" : rack,
		"samples" : samples})

# def receive_samples(request):
# 	"""
# 	Renders receive samples form
# 	"""
# 	if request.method == 'POST':
# 		form = ReceivedSampleForm(request.POST)
# 		if form.is_valid():
# 			form.save()
# 			return HttpResponseRedirect('/receive-samples/')
# 	else:
# 		form = ReceivedSampleForm()
# 	return render(request, 'receive-samples.html', {"form" : form})

# def sample_acks(request):
# 	"""
# 	Renders receive samples form
# 	"""
# 	if request.method == 'POST':
# 		if 'gel1004' in request.POST:
# 			directory = LoadConfig().load()['gel1004path']
# 			for filename in os.listdir(directory):
# 				if filename.endswith(".csv"):
# 					path = directory + filename
# 					with open(path) as csv_file:
# 						csv_reader = csv.reader(csv_file, delimiter=',')
# 						line_count=0
# 						for row in csv_reader:
# 							if line_count == 0:
# 								line_count += 1
# 							else:
# 								Gel1004csv.objects.create(
# 									filename=filename,
# 									participantId=row[0],
# 									groupId=row[1],
# 									diseaseArea=row[2],
# 									gmcRackId=row[3],
# 									clinSampleType=row[4],
# 									glhSampleConsignmentNumber=row[5],
# 									laboratorySampleId=row[6],
# 									laboratoryId=row[7],
# 									laboratorySampleVolume=row[8],
# 									gmcRackWell=row[9],
# 									platingOrganisation=row[10],
# 									priority=row[11],
# 									isProband=row[12])
# 								line_count += 1
# 					os.rename(path, directory + "processed/" + filename)
# 			gel1004 = Gel1004csv.objects.all()
# 			return render(request, 'index.html', {"gel1004" : gel1004})
# 		if 'gel1005' in request.POST:
# 			directory = LoadConfig().load()['gel1005path']
# 			datetime_now = datetime.now(pytz.timezone('Europe/London'))
# 			filename = "ngis_bio_to_gel_samples_received_" + datetime.now(pytz.timezone('Europe/London')).strftime("%y%m%d_%H%M%S") + ".csv"
# 			print(filename)
# 			gel1004_with_matched_samples = Gel1004csv.objects.filter(receivedSample__isnull = False, gel1005__isnull = True)
# 			print(len(gel1004_with_matched_samples))
# 			gel1005s = []
# 			received_racks = set()
# 			for g in gel1004_with_matched_samples:
# 				received_racks.add(g.gmcRackId)
# 				gel1005csv = Gel1005csv.objects.create(
# 					filename=filename,
# 					participantId = g.participantId,
# 					laboratoryId = g.laboratoryId,
# 					sampleReceived = True,
# 					sampleReceivedDateTime = g.receivedSample.sampleReceivedDateTime,
# 					reportGeneratedDateTime = datetime_now,
# 					laboratorySampleId = g.laboratorySampleId)
# 				g.gel1005 = gel1005csv
# 				g.save()
# 				gel1005s.append(gel1005csv)
# 				print(g.participantId)
# 			print(received_racks)
# 			for rack in received_racks:
# 				rack_received_missing_sample = Gel1004csv.objects.filter(gmcRackId = rack, receivedSample__isnull = True, gel1005__isnull = True)
# 				for g in rack_received_missing_sample:
# 					gel1005csv = Gel1005csv.objects.create(
# 						filename=filename,
# 						participantId = g.participantId,
# 						laboratoryId = g.laboratoryId,
# 						sampleReceived = False,
# 						sampleReceivedDateTime = None,
# 						reportGeneratedDateTime = datetime_now,
# 						laboratorySampleId = g.laboratorySampleId)
# 					g.gel1005 = gel1005csv
# 					g.save()
# 					gel1005s.append(gel1005csv)
# 					print(g.participantId)
# 			if gel1005s:
# 				path = directory + filename
# 				with open(path, 'w', newline='') as csvfile:
# 					writer = csv.writer(csvfile, delimiter=',',
# 						quotechar=',', quoting=csv.QUOTE_MINIMAL)
# 					writer.writerow(['Participant ID', 'Laboratory ID',
# 						'Sample Received', 'Sample Received DateTime',
# 						'DateTime Report Generated', 'Laboratory Sample ID'])
# 					for g in gel1005s:
# 						writer.writerow([g.participantId, g.laboratoryId,
# 							g.sampleReceived, g.sampleReceivedDateTime,
# 							g.reportGeneratedDateTime, g.laboratorySampleId])
# 		if 'gel1008' in request.POST:
# 			rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
# 			columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
# 			wells = []
# 			for row in rows:
# 				for column in columns:
# 					wells.append(row + column)
# 			print(wells)	
# 			directory = LoadConfig().load()['gel1008path']
# 			datetime_now = datetime.now(pytz.timezone('Europe/London'))
# 			filename = "ngis_bio_to_gel_sample_dispatch_" + datetime.now(pytz.timezone('Europe/London')).strftime("%y%m%d_%H%M%S") + ".csv"
# 			print(filename)
# 			unplated_samples = Gel1004csv.objects.filter(receivedSample__isnull = False, gel1008__isnull = True)
# 			print(len(unplated_samples))
# 			well_count = 0
# 			gel1008s = []
# 			for g in unplated_samples:
# 				gel1008csv = Gel1008csv.objects.create(
# 							filename = filename,
# 							participantId = g.participantId,
# 							plateId = 'plateID-input',
# 							normalisedBiorepositorySampleVolume = None,
# 							normalisedBiorepositoryConcentration = None,
# 							wellId = wells[well_count],
# 							plateConsignmentNumber = '0000000001',
# 							plateDateOfDispatch = datetime_now)
# 				g.gel1008 = gel1008csv
# 				g.save()
# 				gel1008s.append(gel1008csv)
# 				well_count += 1
# 			if gel1008s:
# 				path = directory + filename
# 				with open(path, 'w', newline='') as csvfile:
# 					writer = csv.writer(csvfile, delimiter=',',
# 						quotechar=',', quoting=csv.QUOTE_MINIMAL)
# 					writer.writerow(['Participant ID', 'Plate ID',
# 						'Normalised Biorepository Sample Volume', 'Normalised Biorepository Concentration',
# 						'Well ID', 'Plate Consignment Number', 'Plate Date of Dispatch'])
# 					for g in gel1008s:
# 						writer.writerow([g.participantId, g.plateId,
# 							g.normalisedBiorepositorySampleVolume, g.normalisedBiorepositoryConcentration,
# 							g.wellId, g.plateConsignmentNumber, g.plateDateOfDispatch])

# 	all_gel1004 = Gel1004csv.objects.filter(receivedSample__isnull = True)
# 	all_received_samples = ReceivedSample.objects.all()
# 	for sample in all_received_samples:
# 		try:
# 			gel1004 = Gel1004csv.objects.get(gmcRackId=sample.gmcRackId, laboratorySampleId=sample.laboratorySampleId)
# 			if gel1004.gmcRackWell == sample.gmcRackWell:
# 				gel1004.receivedSample = sample
# 				gel1004.save()
# 		except:
# 			print("no match")
# 	return render(request, 'sample-acks.html', {
# 		"remaining_gel1004" : all_gel1004})