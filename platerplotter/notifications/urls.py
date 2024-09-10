from django.urls import path

from problemsamples import views as problemsamples_views
from . import views as notifications_view
from .views import import_acks

app_name = 'notifications'

urlpatterns = [
    path('<str:test_status>', notifications_view.import_acks, name='index'),
    path('acknowledge-samples/<str:gel1004>/<str:rack>', notifications_view.acknowledge_samples,
         name='acknowledge_samples'),

    # paths to allow for alernative input directories for unit tests
    path('<str:test_status>', import_acks, name='index'),
    path('acknowledge-samples/<str:gel1004>/<str:rack>/<str:test_status>', notifications_view.acknowledge_samples,
         name='acknowledge_samples'),

]
