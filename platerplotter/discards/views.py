from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DiscardForm
from .models import Discard

@login_required
def discard_view(request):
    current_user = request.user
    discard_form = DiscardForm(request.POST or None, current_user=current_user)
    saved = False

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
        'discard_form': discard_form,
        'saved': saved,
    }
    return render(request, 'discards/discard.html', context=context)
