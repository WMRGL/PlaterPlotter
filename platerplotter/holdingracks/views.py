from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import HoldingRackForm
from .holding_rack_manager import HoldingRackManager
from .models import HoldingRackWell, HoldingRack
from notifications.models import Sample, ReceivingRack
from problemsamples.forms import LogIssueForm, SampleSelectForm
from problemsamples.views import confirm_sample_positions


# Create your views here.


@login_required()
def holding_racks(request, holding_rack_id=None):
	holding_rack_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
	holding_rack_columns = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
	current_holding_racks = HoldingRack.objects.filter(plate__isnull=True).exclude(holding_rack_type='Problem')
	current_holding_racks_dict = {}
	for current_holding_rack in current_holding_racks:
		HoldingRackManager(current_holding_rack).is_half_full()
		HoldingRackManager(current_holding_rack).is_full()
		current_holding_racks_dict[current_holding_rack] = Sample.objects.filter(
			holding_rack_well__holding_rack=current_holding_rack).count()
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
						messages.error(request,
									   "You have scanned an active receiving rack. Please scan an exisiting or new Problem rack.")
						error = True
				except:
					pass
				try:
					holding_rack = HoldingRack.objects.get(holding_rack_id=holding_rack_id, plate__isnull=True)
					if holding_rack.holding_rack_type == "Problem":
						messages.error(request,
									   "You have scanned a holding rack being used for Problem samples. Please scan an exisiting Holding rack.")
						error = True
				except:
					messages.error(request, "Holding rack not found with ID: " + holding_rack_id)
					error = True
				if holding_rack and not error:
					url = reverse('holding_racks', kwargs={
						'holding_rack_id': holding_rack.holding_rack_id,
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
			buffer_wells = HoldingRackWell.objects.filter(holding_rack=holding_rack, buffer_added=True).order_by(
				'well_id')
			holding_rack.ready_to_plate = True
			holding_rack.save()
			messages.info(request, "Holding rack has been marked as ready for plating.")
			if buffer_wells:
				buffer_wells_list = ''
				for buffer_well in buffer_wells:
					buffer_wells_list += buffer_well.well_id + ', '
				messages.warning(request,
								 "Buffer will need to be added to the following wells during plating: " + buffer_wells_list)
		if 'reopen-rack' in request.POST:
			holding_rack_form = HoldingRackForm()
			sample_select_form = SampleSelectForm()
			pk = request.POST['reopen-rack']
			holding_rack = HoldingRack.objects.get(pk=pk)
			holding_rack.ready_to_plate = False
			holding_rack.save()
			buffer_wells = HoldingRackWell.objects.filter(holding_rack=holding_rack, buffer_added=True)
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
					'holding_rack_id': holding_rack.holding_rack_id,
				})
				return HttpResponseRedirect(url)
	else:
		holding_rack_form = HoldingRackForm()
	return render(request, 'holdingracks/holding-racks.html', {
		"holding_rack_form": holding_rack_form,
		"holding_rack": holding_rack,
		"holding_rack_samples": holding_rack_samples,
		"holding_rack_samples_form_dict": holding_rack_samples_form_dict,
		"problem_samples_in_holding_rack": problem_samples_in_holding_rack,
		"assigned_well_list": assigned_well_list,
		"current_holding_racks_dict": current_holding_racks_dict,
		"holding_rack_rows": holding_rack_rows,
		"holding_rack_columns": holding_rack_columns})
