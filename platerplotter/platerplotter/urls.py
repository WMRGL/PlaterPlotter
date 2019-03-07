from django.urls import path

from . import views

urlpatterns = [
    path('', views.import_acks, name='import-acks'),
    path('acknowledge-samples/<str:rack>', views.acknowledge_samples, name='acknowledge_samples'),
    path('awaiting-plating/', views.awaiting_plating, name='awaiting_plating'),
    path('plate-samples/<str:rack>', views.plate_samples, name='plate_samples'),
    path('plate-samples/<str:rack>/<str:plate_id>', views.plate_samples, name='plate_samples'),
    path('ready-to-plate/', views.ready_to_plate, name='ready_to_plate'),
    path('plate-holding-rack/<str:plate_pk>', views.plate_holding_rack, name='plate_holding_rack'),
    path('ready-to-dispatch/', views.ready_to_dispatch, name='ready_to_dispatch'),
]