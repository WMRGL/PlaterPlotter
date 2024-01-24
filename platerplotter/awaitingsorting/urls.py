from django.urls import path

from . views import awaiting_holding_rack_assignment

app_name = 'awaitingsorting'

urlpatterns = [
	path('holding-rack-assignment/', awaiting_holding_rack_assignment, name='awaiting_holding_rack_assignment')
]
