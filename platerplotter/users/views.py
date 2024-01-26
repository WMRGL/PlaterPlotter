from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render

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