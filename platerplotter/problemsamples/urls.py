from django.urls import path

from . import views
app_name = 'problemsamples'

urlpatterns = [
	path('problem-samples/', views.problem_samples, name='problem_samples'),
	path('problem-samples/<str:holding_rack_id>', views.problem_samples, name='problem_samples'),
]
