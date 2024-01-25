from django.urls import path

from . import views

app_name = 'readytoplate'

urlpatterns = [
	path('plate/', views.ready_to_plate, name='ready_to_plate'),
]
