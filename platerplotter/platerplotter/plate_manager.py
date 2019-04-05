from platerplotter.models import Plate, Sample

class PlateManager():

	def __init__(self, plate):
		self.plate = plate
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

	def assign_well(self, sample, well):
		'''
		Finds next available free well and assigns sample to this
		'''
		print("assigning well for sample " + str(sample))
		print("len: " + str(len(self.well_contents)))
		if well:
			well_index = self.well_labels.index(well)
			print(sample)
			sample.plate = self.plate
			sample.plate_well_id = self.well_labels[well_index]
			sample.save()
			print(sample.plate_well_id)
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
					break


