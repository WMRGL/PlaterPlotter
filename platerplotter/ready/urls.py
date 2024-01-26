from django.urls import path

from . import views

app_name = 'ready'

urlpatterns = [
	path('to-plate/', views.ready_to_plate, name='ready_to_plate'),
	path('to-dispatch/', views.ready_to_dispatch, name='ready_to_dispatch'),
	path('for-collection/', views.consignments_for_collection, name='consignments_for_collection'),
	path('audit/', views.audit, name='audit'),

]
