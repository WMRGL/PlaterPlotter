from django.contrib import admin

from holdingracks.models import HoldingRack, HoldingRackWell, Plate
from platerplotter.models import (Gel1008Csv,  Sample)
from notifications.models import Gel1005Csv, Gel1004Csv, ReceivingRack


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


class ReceivingRackAdmin(admin.ModelAdmin):
	model = ReceivingRack
	list_filter = ['laboratory_id', 'disease_area', 'rack_type', 'priority', 'rack_acknowledged']
	list_display = ['receiving_rack_id', 'laboratory_id', 'disease_area', 'rack_type', 'priority']
	search_fields = ['receiving_rack_id']


class HoldingRackAdmin(admin.ModelAdmin):
	model = HoldingRack
	list_filter = ['disease_area', 'holding_rack_type', 'priority']
	list_display = ['holding_rack_id', 'holding_rack_type']
	search_fields = ['holding_rack_id']


class PlateAdmin(admin.ModelAdmin):
	model = Plate
	list_display = ['plate_id', 'gel_1008_csv']
	search_fields = ['plate_id']


class SampleAdmin(admin.ModelAdmin):
	model = Sample
	list_filter = ['disease_area', 'sample_type', 'priority', 'tissue_type',
				   'is_repeat', 'issue_outcome', 'clin_sample_type']
	list_display = ['laboratory_sample_id', 'participant_id', 'group_id',
					'priority', 'sample_type', 'receiving_rack', 'holding_rack_well']
	search_fields = ['laboratory_sample_id', 'participant_id', 'group_id',
					 'holding_rack_well__holding_rack__holding_rack_id',
					 'holding_rack_well__holding_rack__plate__plate_id']


class HoldingRackWellAdmin(admin.ModelAdmin):
	model = HoldingRackWell
	list_display = ['holding_rack', 'well_id', 'buffer_added', 'sample']
	search_fields = ['holding_rack__holding_rack_id', 'holding_rack__plate__plate_id']


admin.site.register(Gel1004Csv, Gel1004CsvAdmin)
admin.site.register(Gel1005Csv, Gel1005CsvAdmin)
admin.site.register(Gel1008Csv, Gel1008CsvAdmin)
admin.site.register(ReceivingRack, ReceivingRackAdmin)
admin.site.register(HoldingRack, HoldingRackAdmin)
admin.site.register(HoldingRackWell, HoldingRackWellAdmin)
admin.site.register(Plate, PlateAdmin)
admin.site.register(Sample, SampleAdmin)
