from django.contrib import admin
from platerplotter.models import Gel1004Csv, Gel1005Csv, Gel1008Csv, Rack, Plate, Sample

class Gel1004CsvAdmin(admin.ModelAdmin):
	model = Gel1004Csv

class Gel1005CsvAdmin(admin.ModelAdmin):
	model = Gel1005Csv

class Gel1008CsvAdmin(admin.ModelAdmin):
	model = Gel1008Csv

class RackAdmin(admin.ModelAdmin):
	model = Rack

class PlateAdmin(admin.ModelAdmin):
	model = Plate

class SampleAdmin(admin.ModelAdmin):
	model = Sample


admin.site.register(Gel1004Csv, Gel1004CsvAdmin)
admin.site.register(Gel1005Csv, Gel1005CsvAdmin)
admin.site.register(Gel1008Csv, Gel1008CsvAdmin)
admin.site.register(Rack, RackAdmin)
admin.site.register(Plate, PlateAdmin)
admin.site.register(Sample, SampleAdmin)
