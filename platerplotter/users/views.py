import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import ProfileUpdateForm


# Create your views here.


def login_user(request):
    """Log user in using Django's authentication system; if successful, redirect to home page.
    :param request:
    :return:
    """
    # filters out Internet Explorer users
    if "MSIE" in request.META['HTTP_USER_AGENT']:
        return render(request, 'platerplotter/incompatible-browser.html')
    else:
        errors = []

        if request.method == 'POST':
            username = request.POST['username'].upper()
            request.session['user'] = username
            password = request.POST['password']
            request.session['password'] = password
            user = authenticate(
                username=username,
                password=password
            )

            if user:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/')
                else:
                    errors.append('Failed to login: account inactive.')
            else:
                errors.append('Failed to login: invalid login details.')

        return render(
            request,
            'users/login.html',
            {
                'errors': errors
            }
        )


def register(request):
    created = False
    matching_users = []
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username'].upper()
        password = request.POST['password']
        matching_users = User.objects.filter(username=username)
        if not matching_users:
            u = User.objects.create_user(username, email, password)
            u.is_active = False
            u.save()
            created = True
    return render(request, 'users/register.html', {'created': created, 'matching_users': matching_users})


def logout_user(request):
    """Log user out using Django's authentication system, and redirect to login page.
    :param request:
    :return:
    """
    logout(request)
    return HttpResponseRedirect('/')


@login_required()
def profile(request):
    user = request.user

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            messages.success(request, f'Your account has been updated!')
            return HttpResponseRedirect(reverse('users:profile'))

    return render(request, 'users/profile.html', {'user': user})


@login_required()
def add_admin(request):
    context = {}
    if request.method == 'POST':
        user_ids = request.POST.get('admins').split(",")
        for user in user_ids:
            user = User.objects.get(id=user)
            group = Group.objects.get(name='Charts')
            user.groups.add(group)
            user.save()
        return HttpResponseRedirect(reverse('users:add_admin'))

    admins = User.objects.filter(groups__name='Charts')

    eligible_users = User.objects.filter(is_active=True, is_staff=False, is_superuser=False).exclude(
        groups__name='Charts')
    context['eligible_users'] = eligible_users
    context['admins'] = admins
    return render(request, 'users/admin.html', context)


@login_required()
def remove_admin(request, pk):
    user = User.objects.get(id=pk)
    group = Group.objects.get(name='Charts')
    user.groups.remove(group)
    user.save()
    return HttpResponseRedirect(reverse('users:add_admin'))
