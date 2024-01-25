from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from holdingracks.holding_rack_manager import HoldingRackManager
from holdingracks.models import HoldingRack
from notifications.models import Sample


# Create your views here.
@login_required()
def ready_to_plate(request):
	"""
	Renders page displaying holding racks that are ready for plating
	"""
	ready_to_plate = HoldingRack.objects.filter(ready_to_plate=True, plate__isnull=True)
	for rack in ready_to_plate:
		HoldingRackManager(rack).is_half_full()
		HoldingRackManager(rack).is_full()
		rack.sample_count = Sample.objects.filter(holding_rack_well__holding_rack=rack).count
	return render(request, 'readytoplate/ready-to-plate.html', {"ready_to_plate": ready_to_plate})


