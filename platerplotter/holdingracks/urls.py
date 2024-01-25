from django.urls import path

from . import views

app_name = 'holdingracks'

urlpatterns = [
	path('racks/', views.holding_racks, name='holding_racks'),
	path('racks/<str:holding_rack_id>', views.holding_racks, name='holding_racks'),
]
