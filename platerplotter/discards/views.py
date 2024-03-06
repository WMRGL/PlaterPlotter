from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DiscardForm
from platerplotter.models import HoldingRack


@login_required
def discard_view(request):
    current_user = request.user
    discard_form = DiscardForm(request.POST or None)

    if request.method == 'POST':
        if discard_form.is_valid():
            obj = discard_form.save(commit=False)
            obj.discarded = True
            obj.save()
            messages.success(request, 'Holding Rack discarded successfully')
            return redirect('discards:discards_index')
        else:
            print(discard_form.errors)
    context = {
        'current_user': current_user,
        'discard_form': discard_form
    }
    return render(request, 'discards/discard.html', context=context)


def discards_index(request):
    holding_racks = HoldingRack.objects.filter(discarded=False)
    discard_racks = []
    current_user = request.user
    discard_form = DiscardForm(request.POST or None)
    query = request.GET.get('q')

    def is_discard_due(holding_rack_id):
        if holding_rack_id.plate:
            dispatch_date = holding_rack_id.plate.gel_1008_csv.date_of_dispatch.date()
            weeks = (date.today() - dispatch_date).days // 7
            return weeks >= 10
        return False

    for holding_rack in holding_racks:
        if is_discard_due(holding_rack):
            discard_racks.append(holding_rack)

    if query:
        results = HoldingRack.objects.filter(Q(holding_rack_id__icontains=query))
        if results:
            for result in results:
                if is_discard_due(result):
                    messages.success(request, 'Holding Rack is due for discard')
                elif result.discarded:
                    messages.success(request, 'Holding Rack has been discarded')
                else:
                    messages.error(request, 'Holding Rack is not due for discard')
        else:
            messages.error(request, 'Holding Rack is not due for discard')

    if request.method == 'POST':
        if discard_form.is_valid():
            selected_racks = request.POST.getlist('selected_rack')
            for rack_id in selected_racks:
                obj = HoldingRack.objects.filter(holding_rack_id=rack_id).last()
                obj.checked_by = discard_form.cleaned_data['checked_by']
                obj.discarded = True
                obj.discarded_by = current_user
                obj.discard_date = datetime.now()
                obj.save()
            messages.success(request, 'Holding Racks discarded successfully')
            return redirect('discards:discards_index')
        else:
            print(discard_form.errors)

    context = {
        'discard_racks': discard_racks,
        'discard_form': discard_form,
        'user': current_user
    }
    return render(request, 'discards/discard.html', context=context)
@login_required()
def all_discards_view(request):
    discards = HoldingRack.objects.filter(discarded=True)

    return render(request, 'discards/all_discards.html', context={'discards': discards})
