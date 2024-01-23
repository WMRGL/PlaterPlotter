import csv
from datetime import datetime
import os
from pathlib import Path

import pytz
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import RackScanner, RackScannerSample
from notifications.models import Sample, ReceivingRack
from platerplotter.config.load_config import LoadConfig
from platerplotter.forms import HoldingRackForm
from platerplotter.models import HoldingRack, HoldingRackWell
from problemsamples.forms import LogIssueForm, ResolveIssueForm, SampleSelectForm
from platerplotter.holding_rack_manager import HoldingRackManager
# Create your views here.


def pad_zeros(well):
	if len(well) == 2:
		return well[0] + '0' + well[1]
	else:
		return well

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
	rack_scanner = RackScanner.objects.filter(scanned_id__iexact=rack_id,
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
def problem_samples(request, holding_rack_id=None, test_status=False):
	holding_rack_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
	holding_rack_columns = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
	samples = Sample.objects.filter(issue_identified=True, issue_outcome="Not resolved").exclude(
		holding_rack_well__holding_rack__holding_rack_type='Problem')
	sample_form_dict = {}
	for sample in samples:
		sample_form_dict[sample] = LogIssueForm(instance=sample)
	current_holding_racks = HoldingRack.objects.filter(holding_rack_type="Problem")
	current_holding_racks_dict = {}
	for current_holding_rack in current_holding_racks:
		current_holding_racks_dict[current_holding_rack] = Sample.objects.filter(
			holding_rack_well__holding_rack=current_holding_rack).count()
	assigned_well_list = []
	holding_rack_samples_form_dict = {}
	holding_rack = None
	holding_rack_samples = None
	if holding_rack_id:
		holding_rack = HoldingRack.objects.get(holding_rack_id=holding_rack_id, holding_rack_type='Problem',
											   plate__isnull=True)
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
						messages.error(request,
									   "You have scanned an active receiving rack. Please scan an exisiting or new Problem rack.")
						error = True
				except:
					pass
				if not error:
					try:
						holding_rack = HoldingRack.objects.get(holding_rack_id=holding_rack_id, plate__isnull=True)
						if holding_rack.holding_rack_type != "Problem":
							messages.error(request,
										   "You have scanned a holding rack being used for " + holding_rack.holding_rack_type + " samples. Please scan an exisiting or new Problem rack.")
							error = True
					except:
						holding_rack = HoldingRack.objects.create(holding_rack_id=holding_rack_id,
																  holding_rack_type="Problem")
						for holding_rack_row in holding_rack_rows:
							for holding_rack_column in holding_rack_columns:
								HoldingRackWell.objects.create(holding_rack=holding_rack,
															   well_id=holding_rack_row + holding_rack_column)
				if holding_rack and not error:
					url = reverse('problem_samples', kwargs={
						'holding_rack_id': holding_rack.holding_rack_id,
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
					'holding_rack_id': holding_rack.holding_rack_id,
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
					'holding_rack_id': holding_rack.holding_rack_id,
				})
				return HttpResponseRedirect(url)
	else:
		holding_rack_form = HoldingRackForm()
		sample_select_form = SampleSelectForm()

	return render(request, 'problemsamples/problem-samples.html', {"sample_form_dict": sample_form_dict,
																  "holding_rack_form": holding_rack_form,
																  "sample_select_form": sample_select_form,
																  "holding_rack": holding_rack,
																  "holding_rack_samples": holding_rack_samples,
																  "holding_rack_samples_form_dict": holding_rack_samples_form_dict,
																  "assigned_well_list": assigned_well_list,
																  "current_holding_racks_dict": current_holding_racks_dict,
																  "holding_rack_rows": holding_rack_rows,
																  "holding_rack_columns": holding_rack_columns})

