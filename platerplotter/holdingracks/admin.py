from django.contrib import admin

from platerplotter.models import HoldingRack
# Register your models here.


class HoldingRackAdmin(admin.ModelAdmin):
	model = HoldingRack
	list_filter = ['disease_area', 'holding_rack_type', 'priority']
	list_display = ['holding_rack_id', 'holding_rack_type']
	search_fields = ['holding_rack_id']


admin.site.register(HoldingRack, HoldingRackAdmin)
