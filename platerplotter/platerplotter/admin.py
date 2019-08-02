from django.contrib import admin
from platerplotter.models import (Gel1004Csv, Gel1005Csv, Gel1008Csv, Rack, 
	Plate, Sample, RackScanner, RackScannerSample, Buffer)

class Gel1004CsvAdmin(admin.ModelAdmin):
	model = Gel1004Csv
	list_filter = ['report_received_datetime']
	list_display = ['filename', 'plating_organisation', 'report_received_datetime']
	search_fields = ['filename']

class Gel1005CsvAdmin(admin.ModelAdmin):
	model = Gel1005Csv
	list_filter = ['report_generated_datetime']
	list_display = ['filename', 'report_generated_datetime']
	search_fields = ['filename']

class Gel1008CsvAdmin(admin.ModelAdmin):
	model = Gel1008Csv
	list_filter = ['report_generated_datetime', 'date_of_dispatch']
	list_display = ['filename', 'consignment_number', 'report_generated_datetime',
					'date_of_dispatch']
	search_fields = ['filename', 'consignment_number']

class RackAdmin(admin.ModelAdmin):
	model = Rack
	list_filter = ['laboratory_id', 'disease_area', 'plate_type', 'priority', 'rack_acknowledged']
	list_display = ['gmc_rack_id', 'laboratory_id', 'disease_area', 'plate_type', 'priority']
	search_fields = ['gmc_rack_id']

class PlateAdmin(admin.ModelAdmin):
	model = Plate
	list_filter = ['disease_area', 'plate_type', 'priority']
	list_display = ['plate_id', 'holding_rack_id', 'plate_type']
	search_fields = ['plate_id', 'holding_rack_id']

class SampleAdmin(admin.ModelAdmin):
	model = Sample
	list_filter = ['disease_area', 'sample_type', 'priority', 'tissue_type', 
					'is_repeat', 'issue_outcome', 'clin_sample_type']
	list_display = ['laboratory_sample_id', 'participant_id', 'group_id',
					'priority', 'sample_type', 'rack', 'plate']
	search_fields = ['laboratory_sample_id', 'participant_id', 'group_id',
					'plate__holding_rack_id', 'plate__plate_id']


class RackScannerAdmin(admin.ModelAdmin):
	model = RackScanner
	list_filter = ['date_modified', 'acknowledged']
	list_display = ['filename', 'scanned_id', 'date_modified', 'acknowledged']
	search_fields = ['filename', 'scanned_id']

class RackScannerSampleAdmin(admin.ModelAdmin):
	model = RackScannerSample
	list_filter = ['rack_scanner']
	list_display = ['sample_id', 'rack_scanner', 'position', 'matched']
	search_fields = ['sample_id']

class BufferAdmin(admin.ModelAdmin):
	model = Buffer
	list_display = ['plate', 'well_id']
	search_fields = ['plate__holding_rack_id', 'plate__plate_id']


admin.site.register(Gel1004Csv, Gel1004CsvAdmin)
admin.site.register(Gel1005Csv, Gel1005CsvAdmin)
admin.site.register(Gel1008Csv, Gel1008CsvAdmin)
admin.site.register(Rack, RackAdmin)
admin.site.register(Plate, PlateAdmin)
admin.site.register(Sample, SampleAdmin)
admin.site.register(Buffer, BufferAdmin)
admin.site.register(RackScanner, RackScannerAdmin)
admin.site.register(RackScannerSample, RackScannerSampleAdmin)

