from django.urls import path

from . import views

urlpatterns = [
    path('', views.import_acks, name='index'),
    path('acknowledge-samples/<str:gel1004>/<str:rack>', views.acknowledge_samples, name='acknowledge_samples'),
    path('problem-samples/', views.problem_samples, name='problem_samples'),
    path('problem-samples/<str:plate_id>', views.problem_samples, name='problem_samples'),
    path('awaiting-holding-rack-assignment/', views.awaiting_holding_rack_assignment, name='awaiting_holding_rack_assignment'),
    path('assign_samples_to_holding_rack/<str:gel1004>/<str:rack>', views.assign_samples_to_holding_rack, name='assign_samples_to_holding_rack'),
    path('assign_samples_to_holding_rack/<str:rack>', views.assign_samples_to_holding_rack, name='assign_samples_to_holding_rack'),
    path('assign_samples_to_holding_rack/<str:gel1004>/<str:rack>/<str:plate_id>', views.assign_samples_to_holding_rack, name='assign_samples_to_holding_rack'),
    path('plate-problem-rack-samples/<str:rack>/<str:plate_id>', views.assign_samples_to_holding_rack, name='assign_problem_samples_to_holding_rack'),
    path('ready-to-plate/', views.ready_to_plate, name='ready_to_plate'),
    path('plate-holding-rack/<str:plate_pk>', views.plate_holding_rack, name='plate_holding_rack'),
    path('ready-to-dispatch/', views.ready_to_dispatch, name='ready_to_dispatch'),
    path('audit/', views.audit, name='audit'),
    path('register/', views.register, name='register'),
]