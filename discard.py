from datetime import date, datetime
from random import sample

from django.contrib.auth.models import User
from django.db import transaction, connection
from platerplotter.models import Plate, HoldingRack, Sample
from discards.views import is_discard_due

user = User.objects.get(username="admin")
holding_racks = HoldingRack.objects.all()
discard_racks = []

for rack in holding_racks:
    rack.checked_by = None
    rack.discarded = False
    rack.discarded_by = None
    rack.discard_date = None
    rack.save()
    Sample.objects.filter(holding_rack_well__holding_rack=rack).update(checked_by=None, discarded=False, discarded_by=None, discard_date=None)


for holding_rack in holding_racks:
    if is_discard_due(holding_rack.plate):
        discard_racks.append(holding_rack)

with transaction.atomic():
    try:
        for discard_rack in discard_racks:
            discard_rack.checked_by = user.username
            discard_rack.discarded = True
            discard_rack.discarded_by = user
            discard_rack.discard_date = datetime.now()
            discard_rack.save()

            sample = Sample.objects.filter(holding_rack_well__holding_rack__pk=discard_rack.pk).update(
                    checked_by=user.username,
                    discarded=True,
                    discarded_by=user,
                    discard_date=datetime.now()
                )
            print(f'{discard_rack} updated successfully')
    except Exception as e:
        print(f"Error updating record: {e}")


