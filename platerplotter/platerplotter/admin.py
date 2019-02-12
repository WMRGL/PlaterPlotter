from django.contrib import admin
from platerplotter.models import Gel1004csv, ReveivedSamples, Gel1005csv

class Gel1004csvAdmin(admin.ModelAdmin):
	model = Gel1004csv

class ReveivedSamplesAdmin(admin.ModelAdmin):
	model = ReveivedSamples

class Gel1005csvAdmin(admin.ModelAdmin):
	model = Gel1005csv

admin.site.register(Gel1004csv, Gel1004csvAdmin)
admin.site.register(ReveivedSamples, ReveivedSamplesAdmin)
admin.site.register(Gel1005csv, Gel1005csvAdmin)