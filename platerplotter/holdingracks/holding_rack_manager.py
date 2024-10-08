from platerplotter.models import HoldingRackWell, Sample
from django.contrib import messages
from django.utils import timezone
from platerplotter.models import Plate

class HoldingRackManager():

    def __init__(self, holding_rack):
        self.holding_rack = holding_rack
        self.holding_rack_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        self.holding_rack_columns = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        self.well_labels = ['A01', 'B01', 'C01', 'D01', 'E01', 'F01', 'G01', 'H01', 'A02', 'B02', 'C02', 'D02',
                            'E02', 'F02', 'G02', 'H02', 'A03', 'B03', 'C03', 'D03', 'E03', 'F03', 'G03', 'H03',
                            'A04', 'B04', 'C04', 'D04', 'E04', 'F04', 'G04', 'H04', 'A05', 'B05', 'C05', 'D05',
                            'E05', 'F05', 'G05', 'H05', 'A06', 'B06', 'C06', 'D06', 'E06', 'F06', 'G06', 'H06',
                            'A07', 'B07', 'C07', 'D07', 'E07', 'F07', 'G07', 'H07', 'A08', 'B08', 'C08', 'D08',
                            'E08', 'F08', 'G08', 'H08', 'A09', 'B09', 'C09', 'D09', 'E09', 'F09', 'G09', 'H09',
                            'A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11',
                            'E11', 'F11', 'G11', 'H11', 'A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12', ]
        self.well_contents = [None, None, None, None, None, None, None, None, None, None, None, None,
                              None, None, None, None, None, None, None, None, None, None, None, None,
                              None, None, None, None, None, None, None, None, None, None, None, None,
                              None, None, None, None, None, None, None, None, None, None, None, None,
                              None, None, None, None, None, None, None, None, None, None, None, None,
                              None, None, None, None, None, None, None, None, None, None, None, None,
                              None, None, None, None, None, None, None, None, None, None, None, None,
                              None, None, None, None, None, None, None, None, None, None, None, None, ]
        self.alt_well_labels = ['A01', 'A02', 'A03', 'A04', 'A05', 'A06', 'A07', 'A08', 'A09', 'A10', 'A11', 'A12',
                                'B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 'B10', 'B11', 'B12',
                                'C01', 'C02', 'C03', 'C04', 'C05', 'C06', 'C07', 'C08', 'C09', 'C10', 'C11', 'C12',
                                'D01', 'D02', 'D03', 'D04', 'D05', 'D06', 'D07', 'D08', 'D09', 'D10', 'D11', 'D12',
                                'E01', 'E02', 'E03', 'E04', 'E05', 'E06', 'E07', 'E08', 'E09', 'E10', 'E11', 'E12',
                                'F01', 'F02', 'F03', 'F04', 'F05', 'F06', 'F07', 'F08', 'F09', 'F10', 'F11', 'F12',
                                'G01', 'G02', 'G03', 'G04', 'G05', 'G06', 'G07', 'G08', 'G09', 'G10', 'G11', 'G12',
                                'H01', 'H02', 'H03', 'H04', 'H05', 'H06', 'H07', 'H08', 'H09', 'H10', 'H11', 'H12', ]
        samples = Sample.objects.filter(holding_rack_well__holding_rack=self.holding_rack)
        for sample in samples:
            well_index = self.well_labels.index(sample.holding_rack_well.well_id)
            if self.well_contents[well_index]:
                raise Exception("Multiple samples have been assigned to same well")
            else:
                self.well_contents[well_index] = sample

    def lookup_alt_index(self, index):
        well_label = self.well_labels[index]
        return self.alt_well_labels.index(well_label)

    def lookup_new_indices(self, indices_to_avoid):
        new_indices_to_avoid = []
        for index in indices_to_avoid:
            well_label = self.alt_well_labels[index]
            new_indices_to_avoid.append(self.well_labels.index(well_label))
        return new_indices_to_avoid

    def determine_indices_to_avoid(self, index):
        '''
		Determines which well positions should be avoided based on the plating rules
		'''
        index = self.lookup_alt_index(index)
        row = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        col_dict = {0: [0, 1, 2], 1: [0, 1, 2, 3], 2: [0, 1, 2, 3, 4], 3: [1, 2, 3, 4, 5],
                    4: [2, 3, 4, 5, 6], 5: [3, 4, 5, 6, 7], 6: [4, 5, 6, 7, 8], 7: [5, 6, 7, 8, 9],
                    8: [6, 7, 8, 9, 10], 9: [7, 8, 9, 10, 11], 10: [8, 9, 10, 11], 11: [9, 10, 11]}
        dict_lookup = col_dict[index % 12]
        indices_to_avoid = [item + ((index // 12) * 12) for item in row]
        well_num = index // 12
        if well_num == 0:  # index in top row
            indices_to_avoid += [(item + ((index // 12) * 12)) + 12 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) + 12 * 2 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) + 12 * 3 for item in dict_lookup]
        elif well_num == 1:  # index in 2nd row
            indices_to_avoid += [(item + ((index // 12) * 12)) + 12 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) + 12 * 2 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) + 12 * 3 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) - 12 for item in dict_lookup]
        elif well_num == 2:  # index in 3rd row
            indices_to_avoid += [(item + ((index // 12) * 12)) + 12 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) + 12 * 2 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) + 12 * 3 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) - 12 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) - 12 * 2 for item in dict_lookup]
        elif 2 < well_num < 5:  # index in a middle rows
            indices_to_avoid += [(item + ((index // 12) * 12)) + 12 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) + 12 * 2 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) + 12 * 3 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) - 12 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) - 12 * 2 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) - 12 * 3 for item in dict_lookup]
        elif well_num == 5:  # index in 6th row
            indices_to_avoid += [(item + ((index // 12) * 12)) + 12 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) + 12 * 2 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) - 12 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) - 12 * 2 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) - 12 * 3 for item in dict_lookup]
        elif well_num == 6:  # index in 7th row
            indices_to_avoid += [(item + ((index // 12) * 12)) + 12 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) - 12 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) - 12 * 2 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) - 12 * 3 for item in dict_lookup]
        elif well_num == 7:  # index in bottom row
            indices_to_avoid += [(item + ((index // 12) * 12)) - 12 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) - 12 * 2 for item in dict_lookup]
            indices_to_avoid += [(item + ((index // 12) * 12)) - 12 * 3 for item in dict_lookup]
        new_indices_to_avoid = self.lookup_new_indices(indices_to_avoid)
        return new_indices_to_avoid

    def assign_holding_rack_well(self, request, sample, well_index):
        if hasattr(sample, 'holding_rack_well'):
            current_well = sample.holding_rack_well
            current_well.sample = None
            current_well.save()
        holding_rack_well = HoldingRackWell.objects.get(
            holding_rack=self.holding_rack,
            well_id=self.well_labels[well_index])
        holding_rack_well.sample = sample
        holding_rack_well.assigned_time = timezone.now()
        holding_rack_well.save()
        messages.info(request, sample.laboratory_sample_id + " assigned to well " + holding_rack_well.well_id)

    def assign_well(self, request, sample, well):
        '''
		Finds next available free well and assigns sample to this
		'''
        if self.holding_rack.holding_rack_type == "Problem":
            if well:
                well_index = self.well_labels.index(well)
                self.assign_holding_rack_well(request, sample, well_index)
            else:
                sample_assigned = False
                well_index = 0
                for well_content in self.well_contents:
                    if well_content:
                        well_index += 1
                    else:
                        self.assign_holding_rack_well(request, sample, well_index)
                        sample_assigned = True
                        break
                if not sample_assigned:
                    messages.error(request, "No more valid positions available in this rack. Please assign " +
                                   sample.laboratory_sample_id + " to a new rack.")
        if self.holding_rack.holding_rack_type == "Proband":
            no_samples_with_same_participant_id = True
            no_family_members_on_same_plate = True
            for well_content in self.well_contents:
                if well_content:
                    if well_content.participant_id == sample.participant_id:
                        no_samples_with_same_participant_id = False
                        messages.error(request, "Unable to add sample " + sample.laboratory_sample_id +
                                       " to this rack as a sample with the same participant ID is already assigned to this rack.")
                    if well_content.group_id == sample.group_id:
                        no_family_members_on_same_plate = False
                        messages.error(request, "Unable to add sample " + sample.laboratory_sample_id +
                                       " to this rack as a sample from the same family is already assigned to this rack.")
            if no_samples_with_same_participant_id and no_family_members_on_same_plate:
                if well:
                    well_index = self.well_labels.index(well)
                    self.assign_holding_rack_well(request, sample, well_index)
                else:
                    sample_assigned = False
                    well_index = 0
                    for well_content in self.well_contents:
                        if well_content:
                            well_index += 1
                        else:
                            self.assign_holding_rack_well(request, sample, well_index)
                            sample_assigned = True
                            break
                    if not sample_assigned:
                        messages.error(request, "No more valid positions available in this rack. Please assign " +
                                       sample.laboratory_sample_id + " to a new rack.")
        elif self.holding_rack.holding_rack_type == "Family":
            matching_proband_sample_found = True
            # all new family samples must have a matching proband except sample_delivery_mode="Family Only" samples
            if sample.is_repeat == "New" and sample.sample_delivery_mode != "Family Only":
                matching_proband_sample_found = False
                matching_proband_samples = Sample.objects.filter(sample_type="Proband", group_id=sample.group_id,
                                                                 holding_rack_well__isnull=True)
                if matching_proband_samples:
                    matching_proband_sample_found = True
                    for matching_proband_sample in matching_proband_samples:
                        messages.warning(request, "Matching proband sample found in GMC rack: " +
                                         matching_proband_sample.receiving_rack.receiving_rack_id + " in well " +
                                         matching_proband_sample.receiving_rack_well + " but not yet assigned to holding rack. These samples must be sent in the same consignment.")
                else:
                    matching_proband_samples = Sample.objects.filter(sample_type="Proband", group_id=sample.group_id,
                                                                     holding_rack_well__holding_rack__plate__gel_1008_csv__isnull=True)
                    if matching_proband_samples:
                        matching_proband_sample_found = True
                        for matching_proband_sample in matching_proband_samples:
                            if matching_proband_sample.holding_rack_well.holding_rack.plate:
                                messages.info(request,
                                              "Matching proband sample found and has already been plated on plate: " +
                                              matching_proband_sample.holding_rack_well.holding_rack.plate.plate_id + " in well " +
                                              matching_proband_sample.holding_rack_well.well_id + ". These samples must be sent in the same consignment.")
                            else:
                                messages.info(request,
                                              "Matching proband sample found and has been assigned to holding rack: " +
                                              matching_proband_sample.holding_rack_well.holding_rack.holding_rack_id + " in well " +
                                              matching_proband_sample.holding_rack_well.well_id + ". These samples must be sent in the same consignment.")
                if not matching_proband_sample_found:
                    messages.error(request,
                                   "No matching proband sample found for this sample. Unable to assign to holding rack.")
            no_samples_with_same_participant_id = True
            well_indices_to_avoid = []
            index_count = 0
            for well_content in self.well_contents:
                if well_content:
                    if well_content.participant_id == sample.participant_id:
                        no_samples_with_same_participant_id = False
                        messages.error(request, "Unable to add sample " + sample.laboratory_sample_id +
                                       " to this rack as a sample with the same participant ID is already assigned to this rack.")
                    elif well_content.group_id == sample.group_id:
                        well_indices_to_avoid += self.determine_indices_to_avoid(index_count)
                index_count += 1
            if matching_proband_sample_found and no_samples_with_same_participant_id:
                for index in well_indices_to_avoid:
                    if not self.well_contents[index]:
                        self.well_contents[index] = 'X'
                if well:
                    well_index = self.well_labels.index(well)
                    if self.well_contents[well_index] == 'X':
                        messages.error(request,
                                       "Selected well is too close to another sample from the same family. Unable to assigned to this well.")
                    else:
                        self.assign_holding_rack_well(request, sample, well_index)
                else:
                    sample_assigned = False
                    well_index = 0
                    for well_content in self.well_contents:
                        if well_content:
                            well_index += 1
                        else:
                            self.assign_holding_rack_well(request, sample, well_index)
                            sample_assigned = True
                            break
                    if not sample_assigned:
                        messages.error(request, "No more valid positions available in this rack. Please assign " +
                                       sample.laboratory_sample_id + " to a new rack.")
        elif self.holding_rack.holding_rack_type == "Tumour":
            matching_germline_sample_found = True
            # all new tumour samples must have a matching germline sample from the same patient except sample_delivery_mode="Tumour First" samples
            if sample.is_repeat == "New" and sample.sample_delivery_mode != "Tumour First":
                matching_germline_sample_found = False
                matching_germline_samples = Sample.objects.filter(sample_type="Cancer Germline",
                                                                  participant_id=sample.participant_id,
                                                                  group_id=sample.group_id,
                                                                  holding_rack_well__isnull=True)
                if matching_germline_samples:
                    matching_germline_sample_found = True
                    for matching_germline_sample in matching_germline_samples:
                        messages.warning(request, "Matching germline sample found in GMC rack: " +
                                         matching_germline_sample.receiving_rack.receiving_rack_id + " in well " +
                                         matching_germline_sample.receiving_rack_well + " but not yet assigned to holding rack. These samples must be sent in the same consignment.")
                else:
                    matching_germline_samples = Sample.objects.filter(sample_type="Cancer Germline",
                                                                      participant_id=sample.participant_id,
                                                                      group_id=sample.group_id,
                                                                      holding_rack_well__holding_rack__plate__gel_1008_csv__isnull=True)
                    if matching_germline_samples:
                        matching_germline_sample_found = True
                        for matching_germline_sample in matching_germline_samples:
                            if matching_germline_sample.holding_rack_well.holding_rack.plate:
                                messages.info(request,
                                              "Matching germline sample found and has already been plated on plate: " +
                                              matching_germline_sample.holding_rack_well.holding_rack.plate.plate_id + " in well " +
                                              matching_germline_sample.holding_rack_well.well_id + ". These samples must be sent in the same consignment.")
                            else:
                                messages.info(request,
                                              "Matching germline sample found and has been assigned to holding rack: " +
                                              matching_germline_sample.holding_rack_well.holding_rack.holding_rack_id + " in well " +
                                              matching_germline_sample.holding_rack_well.well_id + ". These samples must be sent in the same consignment.")
                if not matching_germline_sample_found:
                    messages.error(request,
                                   "No matching germline sample found for this sample. Unable to assign to holding rack.")
            well_indices_to_avoid = []
            index_count = 0
            for well_content in self.well_contents:
                if well_content:
                    if well_content.participant_id == sample.participant_id:
                        well_indices_to_avoid += self.determine_indices_to_avoid(index_count)
                index_count += 1
            if matching_germline_sample_found:
                for index in well_indices_to_avoid:
                    if not self.well_contents[index]:
                        self.well_contents[index] = 'X'
                if well:
                    well_index = self.well_labels.index(well)
                    if self.well_contents[well_index] == 'X':
                        messages.error(request,
                                       "Selected well is too close to another sample from the same family. Unable to assigned to this well.")
                    else:
                        self.assign_holding_rack_well(request, sample, well_index)
                else:
                    sample_assigned = False
                    well_index = 0
                    for well_content in self.well_contents:
                        if well_content:
                            well_index += 1
                        else:
                            self.assign_holding_rack_well(request, sample, well_index)
                            sample_assigned = True
                            break
                    if not sample_assigned:
                        messages.error(request, "No more valid positions available in this rack. Please assign " +
                                       sample.laboratory_sample_id + " to a new rack.")
        elif self.holding_rack.holding_rack_type == "Cancer Germline":
            no_samples_with_same_participant_id = True
            for well_content in self.well_contents:
                if well_content:
                    if well_content.participant_id == sample.participant_id:
                        no_samples_with_same_participant_id = False
                        messages.error(request, "Unable to add sample " + sample.laboratory_sample_id +
                                       " to this rack as a sample with the same participant ID is already assigned to this rack.")
            matching_tumour_sample_found = True
            # all new tumour samples must have a matching germline sample from the same patient except sample_delivery_mode="Germline Late" samples
            if sample.is_repeat == "New" and sample.sample_delivery_mode != "Germline Late":
                matching_tumour_sample_found = False
                matching_tumour_samples = Sample.objects.filter(sample_type="Tumour",
                                                                participant_id=sample.participant_id,
                                                                group_id=sample.group_id,
                                                                holding_rack_well__isnull=True)
                if matching_tumour_samples:
                    matching_tumour_sample_found = True
                    for matching_tumour_sample in matching_tumour_samples:
                        messages.warning(request, "Matching tumour sample found in GMC rack: " +
                                         matching_tumour_sample.receiving_rack.receiving_rack_id + " in well " +
                                         matching_tumour_sample.receiving_rack_well + " but not yet assigned to holding rack. These samples must be sent in the same consignment.")
                else:
                    matching_tumour_samples = Sample.objects.filter(sample_type="Tumour",
                                                                    participant_id=sample.participant_id,
                                                                    group_id=sample.group_id,
                                                                    holding_rack_well__holding_rack__plate__gel_1008_csv__isnull=True)
                    if matching_tumour_samples:
                        matching_tumour_sample_found = True
                        for matching_tumour_sample in matching_tumour_samples:
                            if matching_tumour_sample.holding_rack_well.holding_rack.plate:
                                messages.info(request,
                                              "Matching tumour sample found and has already been plated on plate: " +
                                              matching_tumour_sample.holding_rack_well.holding_rack.plate.plate_id + " in well " +
                                              matching_tumour_sample.holding_rack_well.well_id + ". These samples must be sent in the same consignment.")
                            else:
                                messages.info(request,
                                              "Matching tumour sample found and has been assigned to holding rack: " +
                                              matching_tumour_sample.holding_rack_well.holding_rack.holding_rack_id + " in well " +
                                              matching_tumour_sample.holding_rack_well.well_id + ". These samples must be sent in the same consignment.")
                if not matching_tumour_sample_found:
                    messages.error(request,
                                   "No matching tumour sample found for this sample. Unable to assign to holding rack.")
            if no_samples_with_same_participant_id and matching_tumour_sample_found:
                if well:
                    well_index = self.well_labels.index(well)
                    self.assign_holding_rack_well(request, sample, well_index)
                else:
                    sample_assigned = False
                    well_index = 0
                    for well_content in self.well_contents:
                        if well_content:
                            well_index += 1
                        else:
                            self.assign_holding_rack_well(request, sample, well_index)
                            sample_assigned = True
                            break
                    if not sample_assigned:
                        messages.error(request, "No more valid positions available in this rack. Please assign " +
                                       sample.laboratory_sample_id + " to a new rack.")

    def get_last_occupied_well(self):
        for i, e in enumerate(reversed(self.well_contents)):
            if e is not None:
                return len(self.well_contents) - i - 1
        return -1

    def assign_buffer(self):
        last_occupied_well_index = self.get_last_occupied_well()
        if last_occupied_well_index > 0:
            index_count = 0
            while index_count < last_occupied_well_index:
                if not self.well_contents[index_count]:
                    well_label = self.well_labels[index_count]
                    holding_rack_well = HoldingRackWell.objects.get(
                        holding_rack=self.holding_rack,
                        well_id=self.well_labels[index_count])
                    holding_rack_well.buffer_added = True
                    holding_rack_well.save()
                index_count += 1

    def is_full(self):
        count = 0
        for item in self.well_contents:
            if item:
                count += 1
        if count == 96:
            if not self.holding_rack.full:
                self.holding_rack.full = True
                self.holding_rack.save()
        else:
            if self.holding_rack.full:
                self.holding_rack.full = False
                self.holding_rack.save()

    def is_half_full(self):
        count = 0
        for item in self.well_contents[:48]:
            if item:
                count += 1
        if count == 48:
            if not self.holding_rack.half_full:
                self.holding_rack.half_full = True
                self.holding_rack.save()
        else:
            if self.holding_rack.half_full:
                self.holding_rack.half_full = False
                self.holding_rack.save()
