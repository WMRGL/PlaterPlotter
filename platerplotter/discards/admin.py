from django.contrib import admin

from .models import Discard


# Register your models here.

class DiscardAdmin(admin.ModelAdmin):
	model = Discard

	list_display = ['holding_rack_id', 'discarded_by', 'checked_by', 'dispatch_date']


admin.site.register(Discard, DiscardAdmin)
