from django.urls import path

from . import views

app_name = 'discards'

urlpatterns = [
	path('', views.discard_view, name='discards_index')
]
