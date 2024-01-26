import csv
from datetime import datetime, time
from pathlib import Path

import pytz
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from holdingracks.holding_rack_manager import HoldingRackManager
from holdingracks.models import HoldingRack, Plate, HoldingRackWell
from notifications.models import Sample
from platerplotter.config.load_config import LoadConfig
from ready.forms import Gel1008Form
from holdingracks.forms import PlateSelectForm
from .models import Gel1008Csv


# Create your views here.
@login_required()
def ready_to_plate(request):
	"""
	Renders page displaying holding racks that are ready for plating
	"""
	ready_to_plate = HoldingRack.objects.filter(ready_to_plate=True, plate__isnull=True)
	for rack in ready_to_plate:
		HoldingRackManager(rack).is_half_full()
		HoldingRackManager(rack).is_full()
		rack.sample_count = Sample.objects.filter(holding_rack_well__holding_rack=rack).count
	return render(request, 'ready/ready-to-plate.html', {"ready_to_plate": ready_to_plate})

@login_required()
def ready_to_dispatch(request, test_status=False):
	"""
	Renders page displaying plates that are ready for dispatch
	"""
	ready_to_dispatch = HoldingRack.objects.filter(ready_to_plate=True, plate__isnull=False,
												   plate__gel_1008_csv__isnull=True)
	plate_ids_ready_to_dispatch = []
	plates_ready_to_dispatch = []
	consignment_summaries = {}
	for holding_rack in ready_to_dispatch:
		HoldingRackManager(holding_rack).is_half_full()
		HoldingRackManager(holding_rack).is_full()
		plate_ids_ready_to_dispatch.append(holding_rack.plate.plate_id)
		plates_ready_to_dispatch.append(holding_rack.plate)
		holding_rack.sample_count = Sample.objects.filter(holding_rack_well__holding_rack=holding_rack).count
	if request.method == 'POST':
		if "generate-manifests" in request.POST:
			plate_select_form = PlateSelectForm()
			gel1008_form = Gel1008Form(request.POST)
			selected_plates_list = []
			if gel1008_form.is_valid():
				if request.POST.getlist('selected_plate'):
					plate_pks = request.POST.getlist('selected_plate')
					# determine that all samples that must be sent in the same consignment have been selected
					all_cancer_samples = set()
					all_rare_disease_samples = set()
					for pk in plate_pks:
						plate = Plate.objects.get(pk=pk)
						if plate.holding_rack.holding_rack_type == "Cancer Germline" or plate.holding_rack.holding_rack_type == "Tumour":
							samples = Sample.objects.filter(holding_rack_well__holding_rack__plate=plate)
							for sample in samples:
								all_cancer_samples.add(sample)
						if plate.holding_rack.holding_rack_type == "Proband" or plate.holding_rack.holding_rack_type == "Family":
							samples = Sample.objects.filter(holding_rack_well__holding_rack__plate=plate)
							for sample in samples:
								all_rare_disease_samples.add(sample)
					matching_cancer_samples_not_selected = set()
					for sample in all_cancer_samples:
						matching_samples = Sample.objects.filter(participant_id=sample.participant_id,
																 group_id=sample.group_id,
																 sample_received=True,
																 disease_area='Cancer',
																 holding_rack_well__holding_rack__plate__gel_1008_csv__isnull=True).exclude(
							issue_outcome="Sample returned to extracting GLH").exclude(
							issue_outcome="Sample destroyed")
						for matching_sample in matching_samples:
							if matching_sample not in all_cancer_samples:
								matching_cancer_samples_not_selected.add(matching_sample)
					if matching_cancer_samples_not_selected:
						cancer_sample_info = '<ul>'
						for sample in matching_cancer_samples_not_selected:
							if hasattr(sample, 'holding_rack_well'):
								if sample.holding_rack_well.holding_rack.plate:
									cancer_sample_info += "<li> " + sample.laboratory_sample_id + " in plate " + \
														  sample.holding_rack_well.holding_rack.plate.plate_id + " in well " + \
														  sample.holding_rack_well.well_id + '</li>'
								else:
									cancer_sample_info += "<li> " + sample.laboratory_sample_id + " in holding rack " + \
														  sample.holding_rack_well.holding_rack.holding_rack_id + " in well " + \
														  sample.holding_rack_well.well_id + '</li>'
							else:
								cancer_sample_info += "<li> " + sample.laboratory_sample_id + " in GMC rack " + \
													  sample.receiving_rack.receiving_rack_id + " in well " + \
													  sample.receiving_rack_well + '</li>'
						cancer_sample_info += ' </ul>'
						messages.error(request,
									   "All synchronous multi-tumour samples must be sent in the same consignment. " +
									   "The following samples need to be sent in the same consignment as the plates you have selected:<br>" +
									   cancer_sample_info, extra_tags='safe')
					matching_rare_disease_samples_not_selected = set()
					for sample in all_rare_disease_samples:
						matching_samples = Sample.objects.filter(group_id=sample.group_id,
																 sample_received=True,
																 disease_area='Rare Disease',
																 holding_rack_well__holding_rack__plate__gel_1008_csv__isnull=True).exclude(
							issue_outcome="Sample returned to extracting GLH").exclude(
							issue_outcome="Sample destroyed")
						for matching_sample in matching_samples:
							if matching_sample not in all_rare_disease_samples:
								matching_rare_disease_samples_not_selected.add(matching_sample)
					if matching_rare_disease_samples_not_selected:
						rare_disease_sample_info = '<ul>'
						for sample in matching_rare_disease_samples_not_selected:
							if hasattr(sample, 'holding_rack_well'):
								if sample.holding_rack_well.holding_rack.plate:
									rare_disease_sample_info += "<li> " + sample.laboratory_sample_id + " in plate " + \
																sample.holding_rack_well.holding_rack.plate.plate_id + " in well " + \
																sample.holding_rack_well.well_id + '</li>'
								else:
									rare_disease_sample_info += "<li> " + sample.laboratory_sample_id + " in holding rack " + \
																sample.holding_rack_well.holding_rack.holding_rack_id + " in well " + \
																sample.holding_rack_well.well_id + '</li>'
							else:
								rare_disease_sample_info += "<li> " + sample.laboratory_sample_id + " in GMC rack " + \
															sample.receiving_rack.receiving_rack_id + " in well " + \
															sample.receiving_rack_well + '</li>'
						rare_disease_sample_info += ' </ul>'
						messages.error(request,
									   "All family member samples must be sent in the same consignment as the proband. " +
									   "The following samples need to be sent in the same consignment as the plates you have selected:<br>" +
									   rare_disease_sample_info, extra_tags='safe')
					if not matching_rare_disease_samples_not_selected and not matching_cancer_samples_not_selected:
						consignment_number = gel1008_form.cleaned_data.get('consignment_number')
						date_of_dispatch = gel1008_form.cleaned_data.get('date_of_dispatch')
						matching_gel_1008s = Gel1008Csv.objects.filter(consignment_number=consignment_number)
						error = False
						warning = False
						for matching_gel_1008 in matching_gel_1008s:
							if matching_gel_1008.consignment_collected:
								warning = True
							if matching_gel_1008.date_of_dispatch != date_of_dispatch and not matching_gel_1008.consignment_collected:
								error = True
						if warning:
							messages.warning(request, "Warning, this consignment number has been used before.")
						elif error:
							messages.error(request,
										   "There is an open consignment with this number but the date of dispatch did not match.")
						else:
							if test_status:
								manifest_directory = str(Path.cwd().parent) + '/TestData/Outbound/ConsignmentManifests/'
							else:
								manifest_directory = LoadConfig().load()['consignment_manifest_path']
							for pk in plate_pks:
								datetime_now = datetime.now(pytz.timezone('UTC'))
								filename = "ngis_bio_to_gel_sample_dispatch_" + datetime.now(
									pytz.timezone('UTC')).strftime("%Y%m%d_%H%M%S") + ".csv"
								# need to wait 1 second to make sure filenames for GEL1008s are different
								time.sleep(1)
								gel_1008_csv = Gel1008Csv.objects.create(
									filename=filename,
									report_generated_datetime=datetime_now,
									consignment_number=consignment_number,
									date_of_dispatch=date_of_dispatch)
								plate = Plate.objects.get(pk=pk)
								plate.gel_1008_csv = gel_1008_csv
								plate.save()
								manifest_filename = plate.plate_id + "_" + datetime.now(pytz.timezone('UTC')).strftime(
									"%Y%m%d_%H%M%S") + '.pdf'
								manifest_path = manifest_directory + manifest_filename
								doc = SimpleDocTemplate(manifest_path)
								doc.pagesize = landscape(A4)
								elements = []
								data = [
									['Plate ID', 'Plate Consignment Number', 'Plate Date of Dispatch', 'Type of case',
									 'Well ID', 'Well Type', 'Participant ID', 'Laboratory Sample ID']]
								plate_type = plate.holding_rack.holding_rack_type
								if plate_type == 'Proband':
									type_of_case = 'RP'
								elif plate_type == 'Family':
									type_of_case = 'RF'
								elif plate_type == 'Cancer Germline':
									type_of_case = 'CG'
								elif plate_type == 'Tumour':
									type_of_case = 'CT'
								if test_status:
									gel1008_directory = str(Path.cwd().parent) + '/TestData/Outbound/GEL1008/'
								else:
									if type_of_case == 'RP' or type_of_case == 'CG':
										gel1008_directory = LoadConfig().load()['gel1008path'] + 'RP-CG/'
									else:
										gel1008_directory = LoadConfig().load()['gel1008path'] + 'RF-CT/'
								filename = "ngis_bio_to_gel_sample_dispatch_" + type_of_case + "_" + datetime.now(
									pytz.timezone('UTC')).strftime("%Y%m%d_%H%M%S") + ".csv"
								gel1008_path = gel1008_directory + filename
								with open(gel1008_path, 'w', newline='') as csvfile:
									writer = csv.writer(csvfile, delimiter=',',
														quotechar=',', quoting=csv.QUOTE_MINIMAL)
									writer.writerow(['Plate ID', 'Plate Consignment Number', 'Plate Date of Dispatch',
													 'type_of_case', 'Well ID', 'Well Type', 'Participant ID',
													 'Laboratory Sample ID',
													 'Normalised Biorepository Sample Volume',
													 'Normalised Biorepository Concentration'])
									holding_rack_wells = HoldingRackWell.objects.filter(
										holding_rack=plate.holding_rack).order_by('well_id')
									holding_rack_wells = sorted(holding_rack_wells,
																key=lambda x: (x.well_id[1:], x.well_id[0]))
									for holding_rack_well in holding_rack_wells:
										if holding_rack_well.sample or holding_rack_well.buffer_added:
											plate_id = plate.plate_id
											plate_consignment_number = gel_1008_csv.consignment_number
											plate_date_of_dispatch = gel_1008_csv.date_of_dispatch.replace(
												microsecond=0).isoformat().replace('+00:00', 'Z')
											well_id = holding_rack_well.well_id
											if holding_rack_well.sample and not holding_rack_well.buffer_added:
												well_type = "Sample"
												participant_id = holding_rack_well.sample.participant_id
												laboratory_sample_id = holding_rack_well.sample.laboratory_sample_id
												norm_biorep_sample_vol = holding_rack_well.sample.norm_biorep_sample_vol
												norm_biorep_conc = holding_rack_well.sample.norm_biorep_conc
											elif holding_rack_well.buffer_added and not holding_rack_well.sample:
												well_type = "Buffer"
												participant_id = ""
												laboratory_sample_id = ""
												norm_biorep_sample_vol = ""
												norm_biorep_conc = ""
											else:
												messages.error(request,
															   'Well contents invalid. Reported to contain sample and buffer')
											writer.writerow([plate_id, plate_consignment_number, plate_date_of_dispatch,
															 type_of_case, well_id,
															 well_type, participant_id, laboratory_sample_id,
															 norm_biorep_sample_vol, norm_biorep_conc])
											data.append([plate_id, plate_consignment_number, plate_date_of_dispatch,
														 type_of_case,
														 well_id, well_type, participant_id, laboratory_sample_id])
									flowObjects = list()
									styles = getSampleStyleSheet()
									table_header = "Sample summary for consignment: " + str(consignment_number)
									flowObjects.append(Paragraph(table_header, styles["h4"]))
									t1 = Table(data, hAlign="LEFT")
									t1.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
															('BOX', (0, 0), (-1, -1), 0.25, colors.black),
															('BACKGROUND', (0, 0), (-1, 0), colors.gray),
															('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
															]))
									flowObjects.append(t1)
									doc.build(flowObjects)
									consignment_summaries[manifest_filename] = manifest_path
							manifests = '<ul>'
							print(consignment_summaries)
							for manifest, path in consignment_summaries.items():
								manifests += '<li><a href="/download/' + manifest + '" target="_blank">' + manifest + '</a></li>'
							manifests += '</ul>'
							messages.info(request,
										  "GEL1008 messages have been generated for the following consignment manifests, click to download:<br>" +
										  manifests, extra_tags='safe')
				else:
					messages.warning(request, "No plates selected!")
				return HttpResponseRedirect('/ready-to-dispatch/')
		if "plate" in request.POST:
			gel1008_form = Gel1008Form()
			plate_select_form = PlateSelectForm(request.POST)
			selected_plates = request.POST['selected_plates']
			selected_plates_list = selected_plates.split(',')
			for selected_plate in selected_plates_list:
				if selected_plate == "":
					selected_plates_list.remove(selected_plate)
			selected_plates_list = list(map(int, selected_plates_list))
			if plate_select_form.is_valid():
				plate_id = plate_select_form.cleaned_data.get('plate_id')
				if plate_id in plate_ids_ready_to_dispatch:
					for plate_ready_to_dispatch in plates_ready_to_dispatch:
						if plate_ready_to_dispatch.plate_id == plate_id:
							if plate_ready_to_dispatch.pk in selected_plates_list:
								messages.warning(request, plate_id + " already selected for this consignment.")
							else:
								selected_plates_list.append(plate_ready_to_dispatch.pk)
								messages.info(request, plate_id + " added to the consignment list.")
				else:
					messages.error(request, plate_id + " not found in list of plates ready for dispatch.")
	else:
		selected_plates_list = []
		plate_select_form = PlateSelectForm()
		gel1008_form = Gel1008Form()
	return render(request, 'ready/ready-to-dispatch.html', {
		"ready_to_dispatch": ready_to_dispatch,
		"gel1008_form": gel1008_form,
		"plate_select_form": plate_select_form,
		"selected_plates_list": selected_plates_list})


@login_required()
def consignments_for_collection(request, test_status=False):
	consignments = Gel1008Csv.objects.filter(consignment_collected=False)
	consignment_no_dict = {}
	for gel_1008 in consignments:
		if gel_1008.consignment_number in consignment_no_dict:
			consignment_no_dict[gel_1008.consignment_number].append(Plate.objects.get(gel_1008_csv=gel_1008))
		else:
			consignment_no_dict[gel_1008.consignment_number] = [Plate.objects.get(gel_1008_csv=gel_1008)]
	for consignment, plates in consignment_no_dict.items():
		for plate in plates:
			plate.sample_count = Sample.objects.filter(holding_rack_well__holding_rack__plate=plate).count()
			HoldingRackManager(plate.holding_rack).is_half_full()
			HoldingRackManager(plate.holding_rack).is_full()
	if request.method == 'POST':
		if "send-consignment" in request.POST:
			consignment = request.POST['send-consignment']
			plates = consignment_no_dict[consignment]
			for plate in plates:
				plate.gel_1008_csv.consignment_collected = True
				plate.gel_1008_csv.save()
			messages.info(request, "Consignment collected.")
		return HttpResponseRedirect('/consignments-for-collection/')
	return render(request, 'ready/consignments-for-collection.html', {
		"consignment_no_dict": consignment_no_dict
	})

