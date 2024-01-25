from django.urls import path

from . import views

app_name = 'awaitingsorting'

urlpatterns = [
	path('holding-rack-assignment/', views.awaiting_holding_rack_assignment, name='awaiting_holding_rack_assignment'),
	path('assign-samples-to-holding-rack/<str:gel1004>/<str:rack>', views.assign_samples_to_holding_rack,
		 name='assign_samples_to_holding_rack'),
	path('assign-samples-to-holding-rack/<str:gel1004>/<str:rack>/<str:holding_rack_id>',
		 views.assign_samples_to_holding_rack, name='assign_samples_to_holding_rack'),
	path('assign-samples-to-holding-rack/<str:rack>', views.assign_samples_to_holding_rack,
		 name='assign_samples_to_holding_rack'),


]
