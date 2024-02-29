from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from holdingracks.forms import HoldingRackForm
from holdingracks.holding_rack_manager import HoldingRackManager
from platerplotter.models import HoldingRack, HoldingRackWell
from platerplotter.models import Sample, ReceivingRack
from problemsamples.forms import LogIssueForm, SampleSelectForm
from problemsamples.views import confirm_sample_positions


# Create your views here.
@login_required()
def awaiting_holding_rack_assignment(request):
    unplated_samples = Sample.objects.filter(holding_rack_well__isnull=True,
                                             receiving_rack__gel_1004_csv__gel_1005_csv__isnull=False,
                                             sample_received=True, issue_identified=False)
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
    problem_samples = Sample.objects.filter(holding_rack_well__holding_rack__holding_rack_type="Problem",
                                            issue_outcome="Ready for plating")
    problem_holding_rack_dict = {}
    for problem_sample in problem_samples:
        if problem_sample.holding_rack_well.holding_rack in problem_holding_rack_dict:
            problem_holding_rack_dict[problem_sample.holding_rack_well.holding_rack].append(problem_sample)
        else:
            problem_holding_rack_dict[problem_sample.holding_rack_well.holding_rack] = [problem_sample]
    return render(request, 'awaitingsorting/awaiting-holding-rack-assignment.html', {
        "unplated_racks_dict": unplated_racks_dict,
        "problem_holding_rack_dict": problem_holding_rack_dict})


@login_required()
def assign_samples_to_holding_rack(request, rack, gel1004=None, holding_rack_id=None, current_holding_rack_well=None):
    holding_rack_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    holding_rack_columns = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    # Sample and receiving rack
    if gel1004:
        rack = ReceivingRack.objects.get(gel_1004_csv=gel1004, receiving_rack_id=rack)
        samples = Sample.objects.filter(receiving_rack=rack,
                                        holding_rack_well__isnull=True,
                                        receiving_rack__gel_1004_csv__gel_1005_csv__isnull=False,
                                        sample_received=True).exclude(issue_outcome="Not resolved").exclude(
            issue_outcome="Sample returned to extracting GLH").exclude(
            issue_outcome="Sample destroyed")
        problem_holding_rack = None
    else:
        problem_holding_rack = HoldingRack.objects.get(holding_rack_id=rack, holding_rack_type='Problem')
        samples = Sample.objects.filter(holding_rack_well__holding_rack=problem_holding_rack,
                                        issue_outcome="Ready for plating")
        rack = None
    sample_form_dict = {}
    for sample in samples:
        sample_form_dict[sample] = LogIssueForm(instance=sample)
    # current holding rack
    current_holding_racks = HoldingRack.objects.filter(plate__isnull=True).exclude(holding_rack_type='Problem')
    current_holding_racks_dict = {}
    for current_holding_rack in current_holding_racks:
        HoldingRackManager(current_holding_rack).is_half_full()
        HoldingRackManager(current_holding_rack).is_full()
        current_holding_racks_dict[current_holding_rack] = Sample.objects.filter(
            holding_rack_well__holding_rack=current_holding_rack).count()
    # Sample assignment to rack
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
                        messages.error(request,
                                       "You have scanned an active receiving rack. Please scan an exisiting or new Problem rack.")
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
                        messages.error(request,
                                       "You have scanned a holding rack for Problem samples. Please scan the correct holding rack.")
                        error = True
                except:
                    holding_rack = HoldingRack.objects.create(holding_rack_id=holding_rack_id)
                    for holding_rack_row in holding_rack_rows:
                        for holding_rack_column in holding_rack_columns:
                            HoldingRackWell.objects.create(holding_rack=holding_rack,
                                                           well_id=holding_rack_row + holding_rack_column)
                if holding_rack and not error:
                    if gel1004:
                        url = reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
                            'gel1004': rack.gel_1004_csv.pk,
                            'rack': rack.receiving_rack_id,
                            'holding_rack_id': holding_rack.holding_rack_id,
                        })
                    else:
                        url = reverse('problemsamples:assign_problem_samples_to_holding_rack', kwargs={
                            'rack': problem_holding_rack.holding_rack_id,
                            'holding_rack_id': holding_rack.holding_rack_id,
                        })
                else:
                    if gel1004:
                        url = reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
                            'gel1004': rack.gel_1004_csv.pk,
                            'rack': rack.receiving_rack_id,
                        })
                    else:
                        url = reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
                            'rack': problem_holding_rack.holding_rack_id,
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
            well_A01 = HoldingRackWell.objects.get(holding_rack=holding_rack, well_id='A01')
            if well_A01.sample:
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
            else:
                messages.error(request, "Well A01 must contain a sample")
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
                    if sample.sample_type == holding_rack.holding_rack_type:
                        well = request.POST['well']
                        holding_rack_manager.assign_well(request=request, sample=sample, well=well)
                    else:
                        messages.error(request, "Sample does not match holding rack type! Unable to add to this rack.")
                else:
                    messages.error(request, lab_sample_id + " not found in GLH Rack " + rack.receiving_rack_id)
                if problem_holding_rack:
                    url = reverse('problemsamples:assign_problem_samples_to_holding_rack', kwargs={
                        'rack': problem_holding_rack.holding_rack_id,
                        'holding_rack_id': holding_rack.holding_rack_id,
                    })
                else:
                    url = reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
                        'gel1004': rack.gel_1004_csv.pk,
                        'rack': rack.receiving_rack_id,
                        'holding_rack_id': holding_rack.holding_rack_id,
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
                        url = reverse('problemsamples:assign_problem_samples_to_holding_rack', kwargs={
                            'rack': problem_holding_rack.holding_rack_id,
                            'holding_rack_id': holding_rack.holding_rack_id,
                        })
                    else:
                        url = reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
                            'rack': problem_holding_rack.holding_rack_id,
                        })
                else:
                    if holding_rack:
                        url = reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
                            'gel1004': rack.gel_1004_csv.pk,
                            'rack': rack.receiving_rack_id,
                            'holding_rack_id': holding_rack.holding_rack_id,
                        })
                    else:
                        url = reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
                            'gel1004': rack.gel_1004_csv.pk,
                            'rack': rack.receiving_rack_id,
                        })
                return HttpResponseRedirect(url)
    else:
        holding_rack_form = HoldingRackForm()
        sample_select_form = SampleSelectForm()
    try:
        latest_well = HoldingRackWell.objects.filter(holding_rack=holding_rack).exclude(assigned_time__isnull=True).order_by("-assigned_time")[0].well_id
    except IndexError:
        latest_well = None
    return render(request, 'awaitingsorting/assign-samples-to-holding-rack.html', {
        "rack": rack,
        "problem_holding_rack": problem_holding_rack,
        "samples": samples,
        "holding_rack_form": holding_rack_form,
        "sample_select_form": sample_select_form,
        "sample_form_dict": sample_form_dict,
        "holding_rack": holding_rack,
        "holding_rack_samples": holding_rack_samples,
        "problem_samples_in_holding_rack": problem_samples_in_holding_rack,
        "holding_rack_samples_form_dict": holding_rack_samples_form_dict,
        "assigned_well_list": assigned_well_list,
        "current_holding_racks_dict": current_holding_racks_dict,
        "holding_rack_rows": holding_rack_rows,
        "holding_rack_columns": holding_rack_columns,
        'latest_well': latest_well
    })


@login_required()
def delete_sample(request, gel1004, rack, holding_rack_id, sample_id):
    url = reverse('awaitingsorting:assign_samples_to_holding_rack', kwargs={
        'gel1004': gel1004,
        'rack': rack,
        'holding_rack_id': holding_rack_id,
    })

    try:
        holding_rack_well = get_object_or_404(HoldingRackWell.objects.select_related('sample'), sample__uid=sample_id)
        result = HoldingRackWell.objects.filter(
            holding_rack__holding_rack_type='Problem',
            holding_rack__full=False
        ).select_related('holding_rack').first()

        if result:
            holding_rack_manager = HoldingRackManager(result.holding_rack)
            holding_rack_manager.assign_well(request=request, sample=holding_rack_well.sample, well=None)
        elif not holding_rack_well.sample.issue_identified:
            messages.error(request, 'Kindly log issue to sample')
            return HttpResponseRedirect(url)
        else:
            messages.error(request, 'Problem rack is not available')
            return HttpResponseRedirect(url)

    except HoldingRackWell.DoesNotExist:
        messages.error(request, f"Sample with ID {sample_id} does not exist.")
    return HttpResponseRedirect(url)
