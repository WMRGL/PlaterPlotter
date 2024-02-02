from django.urls import path

from . import views

app_name = 'holdingracks'

urlpatterns = [
	path('racks/', views.holding_racks, name='holding_racks'),
	path('racks/<str:holding_rack_id>', views.holding_racks, name='holding_racks'),
	path('racks/<str:holding_rack_id>/<str:holding_racks_well_id>/', views.holding_racks_well, name='holding_racks_well'),
	path('plate-holding-rack/<str:holding_rack_pk>', views.plate_holding_rack, name='plate_holding_rack'),

]
