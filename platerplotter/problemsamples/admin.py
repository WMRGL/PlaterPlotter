from django.contrib import admin

from platerplotter.models import RackScanner, RackScannerSample


# Register your models here.


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


admin.site.register(RackScanner, RackScannerAdmin)
admin.site.register(RackScannerSample, RackScannerSampleAdmin)
