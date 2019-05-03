from platerplotter.models import Plate, Sample
from django.contrib import messages

class PlateManager():

	def __init__(self, plate):
		self.plate = plate
		self.plate_rows = ['A','B','C','D','E','F','G','H']
		self.plate_columns = ['1','2','3','4','5','6','7','8','9','10','11','12']
		self.well_labels = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 
							'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12',
							'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12',
							'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12',
							'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11', 'E12',
							'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
							'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10', 'G11', 'G12',
							'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12',]
		self.well_contents = [None, None, None, None, None, None, None, None, None, None, None, None, 
					None, None, None, None, None, None, None, None, None, None, None, None,
					None, None, None, None, None, None, None, None, None, None, None, None,
					None, None, None, None, None, None, None, None, None, None, None, None,
					None, None, None, None, None, None, None, None, None, None, None, None,
					None, None, None, None, None, None, None, None, None, None, None, None,
					None, None, None, None, None, None, None, None, None, None, None, None,
					None, None, None, None, None, None, None, None, None, None, None, None,]
		samples = Sample.objects.filter(plate=self.plate)
		print(samples)
		for sample in samples:
			well_index = self.well_labels.index(sample.plate_well_id)
			print(well_index)
			if self.well_contents[well_index]:
				raise Exception("Multiple samples have been assigned to same well")
			else:
				self.well_contents[well_index] = sample
		print(self.well_labels)
		print(self.well_contents)

	def assign_well(self, request, sample, well):
		'''
		Finds next available free well and assigns sample to this
		'''
		print("assigning well for sample " + str(sample))
		print("len: " + str(len(self.well_contents)))
		if self.plate.plate_type == "Proband":
			no_samples_with_same_participant_id = True
			no_family_members_on_same_plate = True
			for well_content in self.well_contents:
				if well_content:
					if well_content.participant_id == sample.participant_id:
						no_samples_with_same_participant_id = False
						messages.error(request, "Unable to add sample " + sample.laboratory_sample_id + " to this rack as a sample with the same participant ID is already assigned to this rack.")
					if well_content.group_id == sample.group_id:
						no_family_members_on_same_plate = False
						messages.error(request, "Unable to add sample " + sample.laboratory_sample_id + " to this rack as a sample from the same family is already assigned to this rack.")
			if no_samples_with_same_participant_id and no_family_members_on_same_plate:
				if well:
					well_index = self.well_labels.index(well)
					print(sample)
					sample.plate = self.plate
					sample.plate_well_id = self.well_labels[well_index]
					sample.save()
					print(sample.plate_well_id)
					messages.info(request, sample.laboratory_sample_id + " assigned to well " + sample.plate_well_id)
				else:
					well_index = 0
					for well_content in self.well_contents:
						print
						print("index count: " + str(well_index))
						if well_content:
							well_index += 1
						else:
							print(sample)
							sample.plate = self.plate
							sample.plate_well_id = self.well_labels[well_index]
							sample.save()
							print(sample.plate_well_id)
							messages.info(request, sample.laboratory_sample_id + " assigned to well " + sample.plate_well_id)
							break
		elif self.plate.plate_type == "Parent":
			matching_proband_sample_found = False
			matching_proband_sample = Sample.objects.filter(sample_type = "Proband", group_id = sample.group_id)
			no_samples_with_same_participant_id = True
			for well_content in self.well_contents:
				if well_content:
					if well_content.participant_id == sample.participant_id:
						no_samples_with_same_participant_id = False
						messages.error(request, "Unable to add sample " + sample.laboratory_sample_id + " to this rack as a sample with the same participant ID is already assigned to this rack.")

			pass
		elif self.plate.plate_type == "Tumour":
			pass
		elif self.plate.plate_type == "Cancer Germline":
			pass



