from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('receive-samples/', views.receive_samples, name='receive-samples')
]