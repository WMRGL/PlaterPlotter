from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from platerplotter.models import Gel1004csv, ReceivedSample, Gel1005csv, Gel1008csv
from platerplotter.config.load_config import LoadConfig
from platerplotter.forms import ReceivedSampleForm
from datetime import datetime
import csv, os
import pytz


def index(request):
	"""
	Renders index page.
	"""
	if request.method == 'POST':
		directory = LoadConfig().load()['gel1004path']
		for filename in os.listdir(directory):
			if filename.endswith(".csv"):
				path = directory + filename
				with open(path) as csv_file:
					csv_reader = csv.reader(csv_file, delimiter=',')
					line_count=0
					for row in csv_reader:
						if line_count == 0:
							line_count += 1
						else:
							Gel1004csv.objects.create(
								filename=filename,
								participantId=row[0],
								groupId=row[1],
								diseaseArea=row[2],
								gmcRackId=row[3],
								clinSampleType=row[4],
								glhSampleConsignmentNumber=row[5],
								laboratorySampleId=row[6],
								laboratoryId=row[7],
								laboratorySampleVolume=row[8],
								gmcRackWell=row[9],
								platingOrganisation=row[10],
								priority=row[11],
								isProband=row[12])
							line_count += 1
				os.rename(path, directory + "processed/" + filename)
		gel1004 = Gel1004csv.objects.all()
		return render(request, 'index.html', {"gel1004" : gel1004})
	
	gel1004 = Gel1004csv.objects.all()

	return render(request, 'index.html', {"gel1004" : gel1004})

def receive_samples(request):
	"""
	Renders receive samples form
	"""
	if request.method == 'POST':
		form = ReceivedSampleForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/receive-samples/')
	else:
		form = ReceivedSampleForm()
	return render(request, 'receive-samples.html', {"form" : form})

def sample_acks(request):
	"""
	Renders receive samples form
	"""
	if request.method == 'POST':
		if 'gel1004' in request.POST:
			directory = LoadConfig().load()['gel1004path']
			for filename in os.listdir(directory):
				if filename.endswith(".csv"):
					path = directory + filename
					with open(path) as csv_file:
						csv_reader = csv.reader(csv_file, delimiter=',')
						line_count=0
						for row in csv_reader:
							if line_count == 0:
								line_count += 1
							else:
								Gel1004csv.objects.create(
									filename=filename,
									participantId=row[0],
									groupId=row[1],
									diseaseArea=row[2],
									gmcRackId=row[3],
									clinSampleType=row[4],
									glhSampleConsignmentNumber=row[5],
									laboratorySampleId=row[6],
									laboratoryId=row[7],
									laboratorySampleVolume=row[8],
									gmcRackWell=row[9],
									platingOrganisation=row[10],
									priority=row[11],
									isProband=row[12])
								line_count += 1
					os.rename(path, directory + "processed/" + filename)
			gel1004 = Gel1004csv.objects.all()
			return render(request, 'index.html', {"gel1004" : gel1004})
		if 'gel1005' in request.POST:
			directory = LoadConfig().load()['gel1005path']
			datetime_now = datetime.now(pytz.timezone('Europe/London'))
			filename = "ngis_bio_to_gel_samples_received_" + datetime.now(pytz.timezone('Europe/London')).strftime("%y%m%d_%H%M%S") + ".csv"
			print(filename)
			gel1004_with_matched_samples = Gel1004csv.objects.filter(receivedSample__isnull = False, gel1005__isnull = True)
			print(len(gel1004_with_matched_samples))
			gel1005s = []
			received_racks = set()
			for g in gel1004_with_matched_samples:
				received_racks.add(g.gmcRackId)
				gel1005csv = Gel1005csv.objects.create(
					filename=filename,
					participantId = g.participantId,
					laboratoryId = g.laboratoryId,
					sampleReceived = True,
					sampleReceivedDateTime = g.receivedSample.sampleReceivedDateTime,
					reportGeneratedDateTime = datetime_now,
					laboratorySampleId = g.laboratorySampleId)
				g.gel1005 = gel1005csv
				g.save()
				gel1005s.append(gel1005csv)
				print(g.participantId)
			print(received_racks)
			for rack in received_racks:
				rack_received_missing_sample = Gel1004csv.objects.filter(gmcRackId = rack, receivedSample__isnull = True, gel1005__isnull = True)
				for g in rack_received_missing_sample:
					gel1005csv = Gel1005csv.objects.create(
						filename=filename,
						participantId = g.participantId,
						laboratoryId = g.laboratoryId,
						sampleReceived = False,
						sampleReceivedDateTime = None,
						reportGeneratedDateTime = datetime_now,
						laboratorySampleId = g.laboratorySampleId)
					g.gel1005 = gel1005csv
					g.save()
					gel1005s.append(gel1005csv)
					print(g.participantId)
			if gel1005s:
				path = directory + filename
				with open(path, 'w', newline='') as csvfile:
					writer = csv.writer(csvfile, delimiter=',',
						quotechar=',', quoting=csv.QUOTE_MINIMAL)
					writer.writerow(['Participant ID', 'Laboratory ID',
						'Sample Received', 'Sample Received DateTime',
						'DateTime Report Generated', 'Laboratory Sample ID'])
					for g in gel1005s:
						writer.writerow([g.participantId, g.laboratoryId,
							g.sampleReceived, g.sampleReceivedDateTime,
							g.reportGeneratedDateTime, g.laboratorySampleId])
		if 'gel1008' in request.POST:
			rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
			columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
			wells = []
			for row in rows:
				for column in columns:
					wells.append(row + column)
			print(wells)	
			directory = LoadConfig().load()['gel1008path']
			datetime_now = datetime.now(pytz.timezone('Europe/London'))
			filename = "ngis_bio_to_gel_sample_dispatch_" + datetime.now(pytz.timezone('Europe/London')).strftime("%y%m%d_%H%M%S") + ".csv"
			print(filename)
			unplated_samples = Gel1004csv.objects.filter(receivedSample__isnull = False, gel1008__isnull = True)
			print(len(unplated_samples))
			well_count = 0
			gel1008s = []
			for g in unplated_samples:
				gel1008csv = Gel1008csv.objects.create(
							filename = filename,
							participantId = g.participantId,
							plateId = 'plateID-input',
							normalisedBiorepositorySampleVolume = None,
							normalisedBiorepositoryConcentration = None,
							wellId = wells[well_count],
							plateConsignmentNumber = '0000000001',
							plateDateOfDispatch = datetime_now)
				g.gel1008 = gel1008csv
				g.save()
				gel1008s.append(gel1008csv)
				well_count += 1
			if gel1008s:
				path = directory + filename
				with open(path, 'w', newline='') as csvfile:
					writer = csv.writer(csvfile, delimiter=',',
						quotechar=',', quoting=csv.QUOTE_MINIMAL)
					writer.writerow(['Participant ID', 'Plate ID',
						'Normalised Biorepository Sample Volume', 'Normalised Biorepository Concentration',
						'Well ID', 'Plate Consignment Number', 'Plate Date of Dispatch'])
					for g in gel1008s:
						writer.writerow([g.participantId, g.plateId,
							g.normalisedBiorepositorySampleVolume, g.normalisedBiorepositoryConcentration,
							g.wellId, g.plateConsignmentNumber, g.plateDateOfDispatch])

	all_gel1004 = Gel1004csv.objects.filter(receivedSample__isnull = True)
	return render(request, 'sample-acks.html', {
		"remaining_gel1004" : all_gel1004})