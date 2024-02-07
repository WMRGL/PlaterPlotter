import datetime
from datetime import date

from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DiscardForm
from platerplotter.models import HoldingRack

@login_required
def discard_view(request):
    current_user = request.user
    discard_form = DiscardForm(request.POST or None, current_user=current_user)

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

@login_required()
def discards_index(request):
    context = {}
    holding_racks = HoldingRack.objects.all()
    discard_racks = []
    current_user = request.user
    discard_form = DiscardForm(request.POST or None)

    for holding_rack in holding_racks:
        if holding_rack.plate and holding_rack.discarded == False:
            dispatch_date = holding_rack.plate.gel_1008_csv.date_of_dispatch.date()
            today = date.today()
            weeks = (today - dispatch_date).days // 7
            if weeks > 9:
                discard_racks.append(holding_rack)
        else:
            pass

    if request.method == 'POST':
        if discard_form.is_valid():
            obj = HoldingRack.objects.filter(holding_rack_id=discard_form.cleaned_data['holding_rack_id']).last()
            obj.checked_by = discard_form.cleaned_data['checked_by']
            obj.discarded = discard_form.cleaned_data['discarded']
            obj.discarded_by = current_user
            obj.discard_date = datetime.datetime.now()
            obj.save()
            messages.success(request, 'Holding Rack discarded successfully')
            return redirect('discards:discards_index')
        else:
            print(discard_form.errors)
    context['discard_racks'] = discard_racks
    context['discard_form'] = discard_form
    context['user'] = current_user
    return render(request, 'discards/discard.html', context=context)
