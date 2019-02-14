from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from platerplotter.models import Gel1004csv, ReceivedSamples, ReceivedSample
from platerplotter.config.load_config import LoadConfig
from platerplotter.forms import ReceivedSamplesForm, ReceivedSampleForm
import csv, os


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
	
	all_gel1004 = Gel1004csv.objects.all()
	all_received_samples = ReceivedSample.objects.all()
	matches = []
	partial_matches = []
	sample_no_gel1004 = []
	gel1004_no_sample = []
	for sample in all_received_samples:
		try:
			gel1004 = Gel1004csv.objects.get(gmcRackId=sample.gmcRackId, laboratorySampleId=sample.laboratorySampleId)
			if gel1004.gmcRackWell == sample.gmcRackWell:
				matches.append((gel1004, sample))
			else:
				partial_matches.append((gel1004, sample))
			all_gel1004 = all_gel1004.remove(gel1004)
			all_received_samples = all_received_samples.remove(sample)
		except:
			print("no match")
	return render(request, 'sample-acks.html', {
		"remaining_gel1004" : all_gel1004,
		"remaining_samples" : all_received_samples,
		"matches" : matches,
		"partial_matches" : partial_matches})