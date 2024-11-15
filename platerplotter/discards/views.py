from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.db.transaction import atomic
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .forms import DiscardForm
from platerplotter.models import HoldingRack, HoldingRackWell, Sample


# Function to check if a plate is due for discard
def is_discard_due(plate):
    # Check if plate or necessary attributes are None
    if plate is None or not hasattr(plate, 'gel_1008_csv') or not hasattr(plate.gel_1008_csv, 'date_of_dispatch'):
        return False

    # Ensure date_of_dispatch is not None and is a datetime or date
    dispatch_date = plate.gel_1008_csv.date_of_dispatch
    if dispatch_date is None:
        return False

    # If dispatch_date is datetime, convert to date
    if isinstance(dispatch_date, datetime):
        dispatch_date = dispatch_date.date()
    elif not isinstance(dispatch_date, date):
        return False

    # Calculate the number of weeks since dispatch_date
    today_date = date.today()
    weeks = (today_date - dispatch_date).days // 7
    return weeks >= 10


@login_required()
def discards_index(request):
    holding_racks = HoldingRack.objects.filter(discarded=False)
    discard_racks = []
    current_user = request.user
    discard_form = DiscardForm(request.POST or None)
    query = request.GET.get('q')

    # Iterate through holding racks to find those due for discard
    for holding_rack in holding_racks:
        if is_discard_due(holding_rack.plate):
            discard_racks.append({
                'holding_rack_id': holding_rack,
                'total': HoldingRackWell.objects.filter(sample__isnull=False, holding_rack=holding_rack).count()
            })

    # Handling search query
    if query:
        result = HoldingRack.objects.filter(Q(holding_rack_id__icontains=query)).last()
        if result:
            if result.discarded:
                messages.error(request, 'Holding Rack has been discarded')
            elif is_discard_due(result.plate):
                messages.success(request, 'Holding Rack is due for discard')
            else:
                messages.error(request, 'Holding Rack is not due for discard')
        else:
            messages.error(request, 'Holding Rack is not due for discard')

    # Handle form submission
    if request.method == 'POST':
        if discard_form.is_valid():
            selected_racks = request.POST.getlist('selected_rack')
            with transaction.atomic():
                for rack_id in selected_racks:
                    obj = HoldingRack.objects.filter(holding_rack_id=rack_id).last()
                    obj.checked_by = discard_form.cleaned_data['checked_by']
                    obj.discarded = True
                    obj.discarded_by = current_user
                    obj.discard_date = datetime.now()
                    obj.save()

                    # Bulk update all samples with same holding rack
                    Sample.objects.filter(holding_rack_well__holding_rack__holding_rack_id=rack_id).update(
                        checked_by=discard_form.cleaned_data['checked_by'],
                        discarded=True,
                        discarded_by=current_user,
                        discard_date=datetime.now()
                    )

                messages.success(request, 'Holding Racks discarded successfully')
            return redirect('discards:discards_index')

    context = {
        'discard_racks': discard_racks,
        'discard_form': discard_form,
        'user': current_user
    }

    return render(request, 'discards/discard.html', context=context)


@login_required()
def all_discards_view(request):
    data = HoldingRack.objects.filter(discarded=True)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search = request.GET.get('search[value]', '')

        if search:
            data = HoldingRack.objects.filter(discarded=True, holding_rack_id__icontains=search)

        # Apply pagination to the queryset
        total_records = data.count()
        filtered_records = total_records
        data = data[start:start + length]

        response = {
            'draw': int(request.GET.get('draw', 0)),
            'recordsTotal': total_records,
            'recordsFiltered': filtered_records,
            'data': [
                [
                    item.holding_rack_id,
                    item.plate.gel_1008_csv.date_of_dispatch.strftime('%Y-%m-%d'),
                    item.discarded,
                    item.discarded_by.first_name + ' ' + item.discarded_by.last_name
                    if item.discarded_by.first_name or item.discarded_by.last_name else item.discarded_by.username,
                    item.checked_by,
                    item.discard_date.strftime('%Y-%m-%d'),
                ] for item in data
            ]
        }

        return JsonResponse(response)
    return render(request, 'discards/all_discards.html', {'data': data})
