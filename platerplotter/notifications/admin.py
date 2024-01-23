from django.contrib import admin

from .models import Gel1005Csv, Gel1004Csv, Sample

# Register your models here.


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


class SampleAdmin(admin.ModelAdmin):
	model = Sample
	list_filter = ['disease_area', 'sample_type', 'priority', 'tissue_type',
				   'is_repeat', 'issue_outcome', 'clin_sample_type']
	list_display = ['laboratory_sample_id', 'participant_id', 'group_id',
					'priority', 'sample_type', 'receiving_rack', 'holding_rack_well']
	search_fields = ['laboratory_sample_id', 'participant_id', 'group_id',
					 'holding_rack_well__holding_rack__holding_rack_id',
					 'holding_rack_well__holding_rack__plate__plate_id']


admin.site.register(Gel1004Csv, Gel1004CsvAdmin)
admin.site.register(Gel1005Csv, Gel1005CsvAdmin)
admin.site.register(Sample, SampleAdmin)
