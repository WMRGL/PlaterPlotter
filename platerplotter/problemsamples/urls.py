from django.urls import path

from . import views
app_name = 'problemsamples'

urlpatterns = [
	path('samples/', views.problem_samples, name='samples'),
	path('samples/<str:holding_rack_id>', views.problem_samples, name='problem_samples'),
	path('assign-problem-rack-samples-to-holding-rack/<str:rack>/<str:holding_rack_id>',
		 views.assign_samples_to_holding_rack, name='assign_problem_samples_to_holding_rack'), #Not done
]
