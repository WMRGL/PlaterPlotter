from django.contrib import admin
from platerplotter.models import Gel1004csv, ReceivedSamples, Gel1005csv

class Gel1004csvAdmin(admin.ModelAdmin):
	model = Gel1004csv

class ReceivedSamplesAdmin(admin.ModelAdmin):
	model = ReceivedSamples

class Gel1005csvAdmin(admin.ModelAdmin):
	model = Gel1005csv

admin.site.register(Gel1004csv, Gel1004csvAdmin)
admin.site.register(ReceivedSamples, ReceivedSamplesAdmin)
admin.site.register(Gel1005csv, Gel1005csvAdmin)