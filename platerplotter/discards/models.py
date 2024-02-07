from django.db import models
from django.conf import settings

from platerplotter.models import HoldingRack


# Create your models here.


class Discard(models.Model):
	holding_rack = models.ForeignKey(HoldingRack, on_delete=models.SET_NULL, null=True, blank=True)
	discarded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	checked_by = models.CharField(max_length=255)
	dispatch_date = models.DateField()
	discarded = models.BooleanField(default=False)
	created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.holding_rack)

	@property
	def discarded_by_name(self):
		return f"{self.discarded_by.first_name} {self.discarded_by.last_name}"

	class Meta:
		db_table = 'Discard'
		verbose_name = 'Discard'
		verbose_name_plural = 'Discards'
