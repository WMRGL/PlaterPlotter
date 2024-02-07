from django.urls import path

from . import views

app_name = 'discards'

urlpatterns = [
	path('', views.discards_index, name='discards_index'),
]
