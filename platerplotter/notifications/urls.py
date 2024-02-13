from django.urls import path

from . import views


app_name = 'notifications'

urlpatterns = [
	path('<str:test_status>', views.import_acks, name='index'),
	path('acknowledge-samples/<str:gel1004>/<str:rack>', views.acknowledge_samples, name='acknowledge_samples')
]
