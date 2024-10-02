from datetime import date, datetime
from django.contrib.auth.models import User
from django.db import transaction, connection
from platerplotter.models import Plate, HoldingRack, Sample
from discards.views import is_discard_due

user = User.objects.get(username="admin")
holding_racks = HoldingRack.objects.all()
discard_racks = []

for holding_rack in holding_racks:
    if is_discard_due(holding_rack.plate):
        discard_racks.append(holding_rack)
        print(holding_rack)

with transaction.atomic():
    for discard_rack in discard_racks:
        try:
            objects = HoldingRack.objects.filter(holding_rack_id=discard_rack.holding_rack_id)
            for obj in objects:
                obj.checked_by = user.username
                obj.discarded = True
                obj.discarded_by = user
                obj.discard_date = datetime.now()
                obj.save()

                # Bulk update all samples with same holding rack
                Sample.objects.filter(holding_rack_well__holding_rack=obj).update(
                    checked_by=user.username,
                    discarded=True,
                    discarded_by=user,
                    discard_date=datetime.now()
                )
                print(f'{obj} updated successfully')
        except Exception as e:
            print(f"Error updating record: {e}")
            break
