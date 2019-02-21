from django.urls import path

from . import views

urlpatterns = [
    path('', views.import_acks, name='import-acks'),
    path('acknowledge-samples/<str:rack>', views.acknowledge_samples, name='acknowledge-samples'),
    #path('receive-samples/', views.receive_samples, name='receive-samples'),
    #path('sample-acks/', views.sample_acks, name='sample-acks'),
]