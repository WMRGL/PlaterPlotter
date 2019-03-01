from django.urls import path

from . import views

urlpatterns = [
    path('', views.import_acks, name='import-acks'),
    path('acknowledge-samples/<str:rack>', views.acknowledge_samples, name='acknowledge_samples'),
    path('awaiting-plating/', views.awaiting_plating, name='awaiting_plating'),
    path('plate-samples/<str:rack>', views.plate_samples, name='plate_samples'),
    path('plate-samples/<str:rack>/<str:plate_id>', views.plate_samples, name='plate_samples'),
    #path('receive-samples/', views.receive_samples, name='receive-samples'),
    #path('sample-acks/', views.sample_acks, name='sample-acks'),
]