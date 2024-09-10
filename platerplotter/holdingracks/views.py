import csv
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from awaitingsorting.views import return_rack_clean
from notifications.views import confirm_sample_positions
from platerplotter.config.load_config import LoadConfig
from platerplotter.models import HoldingRackWell, HoldingRack, Plate
from platerplotter.models import Sample, ReceivingRack
from problemsamples.forms import LogIssueForm, SampleSelectForm
from .forms import HoldingRackForm, PlatingForm
from .holding_rack_manager import HoldingRackManager


# Create your views here.

def strip_zeros(well):
    if well[1] == '0':
        return well[0] + well[2]
    else:
        return well


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
                    url = reverse('holdingracks:holding_racks', kwargs={
                        'holding_rack_id': holding_rack.holding_rack_id,
                    })
                else:
                    url = reverse('holdingracks:holding_racks')
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
                url = reverse('holdingracks:holding_racks', kwargs={
                    'holding_rack_id': holding_rack.holding_rack_id,
                })
                return HttpResponseRedirect(url)

        if 'return_rack' in request.POST:
            url = reverse('holdingracks:holding_racks', kwargs={
                'holding_rack_id': holding_rack.holding_rack_id,
            })
            return_sample = request.POST['return_sample']
            return_problem_rack_id = request.POST['return_holding_rack']
            sample = get_object_or_404(Sample, laboratory_sample_id=return_sample)
            try:
                receiving_rack = ReceivingRack.objects.get(receiving_rack_id=return_problem_rack_id)
            except ReceivingRack.MultipleObjectsReturned:
                receiving_rack = ReceivingRack.objects.filter(receiving_rack_id=return_problem_rack_id).first()
            except ReceivingRack.DoesNotExist:
                receiving_rack = None

            if receiving_rack:
                messages.error(request, "You have scanned a receiving rack. "
                                        "Please scan an existing or a new Problem rack")
                return HttpResponseRedirect(url)

            problem_rack_id = return_rack_clean(return_problem_rack_id)
            problem_rack, created = HoldingRack.objects.get_or_create(holding_rack_id=problem_rack_id,
                                                                      holding_rack_type='Problem')
            if created:
                for holding_rack_row in holding_rack_rows:
                    for holding_rack_column in holding_rack_columns:
                        HoldingRackWell.objects.create(holding_rack=problem_rack,
                                                       well_id=holding_rack_row + holding_rack_column)

            if not sample.issue_identified:
                messages.error(request, 'Kindly log issue to sample')
                return HttpResponseRedirect(url)

            holding_rack_manager = HoldingRackManager(problem_rack)
            holding_rack_manager.assign_well(request=request, sample=sample, well=None)
            url = reverse("problemsamples:problem_samples", kwargs={"holding_rack_id": problem_rack.holding_rack_id})
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


@login_required()
def holding_racks_well(request, holding_rack_id=None, holding_racks_well_id=None):
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
                    url = reverse('holdingracks:holding_racks', kwargs={
                        'holding_rack_id': holding_rack.holding_rack_id,
                    })
                else:
                    url = reverse('holdingracks:holding_racks')
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
                url = reverse('holdingracks:holding_racks', kwargs={
                    'holding_rack_id': holding_rack.holding_rack_id,
                })
                return HttpResponseRedirect(url)
    else:
        holding_rack_form = HoldingRackForm()
    return render(request, 'holdingracks/holding-racks-well.html', {
        "holding_rack_form": holding_rack_form,
        "holding_rack": holding_rack,
        "holding_rack_samples": holding_rack_samples,
        "holding_rack_samples_form_dict": holding_rack_samples_form_dict,
        "problem_samples_in_holding_rack": problem_samples_in_holding_rack,
        "assigned_well_list": assigned_well_list,
        "current_holding_racks_dict": current_holding_racks_dict,
        "holding_rack_rows": holding_rack_rows,
        "holding_rack_columns": holding_rack_columns,
        "holding_racks_well_id": holding_racks_well_id
    })


@login_required()
def plate_holding_rack(request, holding_rack_pk, test_status=False):
    holding_rack = HoldingRack.objects.get(pk=holding_rack_pk)
    samples = Sample.objects.filter(holding_rack_well__holding_rack=holding_rack)
    if request.method == 'POST':
        if "rack-scanner" in request.POST:
            plating_form = PlatingForm()
            confirm_sample_positions(request, holding_rack, samples, final_check=True)
        if "assign-plate" in request.POST:
            plating_form = PlatingForm(request.POST)
            if plating_form.is_valid():
                plate_id = plating_form.cleaned_data.get('plate_id')
                plate = Plate.objects.create(plate_id=plate_id)
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
                                well_contents = "NO READ"  # previously read "BUFFER" but Hamilton robot needs reprogramming
                            else:
                                messages.error(request, 'Well contents invalid. Reported to contain sample and buffer')
                        else:
                            well_contents = "NO READ"
                        writer.writerow([well_id, well_contents, ' 2d_rackid_1', holding_rack.holding_rack_id])
    else:
        plating_form = PlatingForm()

    try:
        latest_well = \
            HoldingRackWell.objects.filter(holding_rack=holding_rack).exclude(assigned_time__isnull=True).order_by(
                "-assigned_time")[0].well_id
    except IndexError:
        latest_well = None
    return render(request, 'holdingracks/plate-holding-rack.html', {
        "holding_rack": holding_rack,
        "samples": samples,
        "plating_form": plating_form,
        "latest_well": latest_well
    })


@login_required()
def delete_sample(request, gel1004, rack, holding_rack_id, sample_id):
    url = reverse('holdingracks:holding_racks', kwargs={
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
