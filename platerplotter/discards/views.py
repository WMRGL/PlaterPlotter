from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .forms import DiscardForm
from platerplotter.models import HoldingRack


def discards_index(request):
    holding_racks = HoldingRack.objects.filter(discarded=False)
    discard_racks = []
    current_user = request.user
    discard_form = DiscardForm(request.POST or None)
    query = request.GET.get('q')

    # Function to check if a plate is due for discard
    def is_discard_due(plate):
        if plate:
            dispatch_date = plate.gel_1008_csv.date_of_dispatch.date()
            weeks = (date.today() - dispatch_date).days // 7
            return weeks >= 10
        return False

    # Iterate through holding racks to find those due for discard
    for holding_rack in holding_racks:
        if is_discard_due(holding_rack.plate):
            discard_racks.append(holding_rack)

    # Handling search query
    if query:
        results = HoldingRack.objects.filter(Q(holding_rack_id__icontains=query))
        if results:
            for result in results:
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
            for rack_id in selected_racks:
                obj = HoldingRack.objects.filter(holding_rack_id=rack_id).last()
                # Update rack information after discard
                obj.checked_by = discard_form.cleaned_data['checked_by']
                obj.discarded = True
                obj.discarded_by = current_user
                obj.discard_date = datetime.now()
                obj.save()
            messages.success(request, 'Holding Racks discarded successfully')
            return redirect('discards:discards_index')
        else:
            print(discard_form.errors)

    # Pagination
    paginator = Paginator(discard_racks, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'discard_racks': page_obj,
        'discard_form': discard_form,
        'user': current_user
    }

    return render(request, 'discards/discard.html', context=context)
@login_required()
def all_discards_view(request):
    discards = HoldingRack.objects.filter(discarded=True)

    return render(request, 'discards/all_discards.html', context={'discards': discards})
