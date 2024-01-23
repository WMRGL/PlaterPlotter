from django.urls import path
from django.urls import include


from . import views
from notifications.views import import_acks, post_volume_check

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', import_acks, name='index'),
    path('acknowledge-samples/<str:gel1004>/<str:rack>', views.acknowledge_samples, name='acknowledge_samples'),
    path('post/ajax/volume', post_volume_check, name = "post_volume_check"),
    path('problem-samples/', views.problem_samples, name='problem_samples'),
    path('problem-samples/<str:holding_rack_id>', views.problem_samples, name='problem_samples'),
    path('awaiting-holding-rack-assignment/', views.awaiting_holding_rack_assignment, name='awaiting_holding_rack_assignment'),
    path('assign-samples-to-holding-rack/<str:gel1004>/<str:rack>', views.assign_samples_to_holding_rack, name='assign_samples_to_holding_rack'),
    path('assign-samples-to-holding-rack/<str:rack>', views.assign_samples_to_holding_rack, name='assign_samples_to_holding_rack'),
    path('assign-samples-to-holding-rack/<str:gel1004>/<str:rack>/<str:holding_rack_id>', views.assign_samples_to_holding_rack, name='assign_samples_to_holding_rack'),
    path('assign-problem-rack-samples-to-holding-rack/<str:rack>/<str:holding_rack_id>', views.assign_samples_to_holding_rack, name='assign_problem_samples_to_holding_rack'),
    path('holding-racks/', views.holding_racks, name='holding_racks'),
    path('holding-racks/<str:holding_rack_id>', views.holding_racks, name='holding_racks'),
    path('ready-to-plate/', views.ready_to_plate, name='ready_to_plate'),
    path('plate-holding-rack/<str:holding_rack_pk>', views.plate_holding_rack, name='plate_holding_rack'),
    path('ready-to-dispatch/', views.ready_to_dispatch, name='ready_to_dispatch'),
    path('consignments-for-collection/', views.consignments_for_collection, name='consignments_for_collection'),
    path('audit/', views.audit, name='audit'),
    path('register/', views.register, name='register'),
    path('download/<str:filename>', views.download_manifest, name='download_manifest'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    # paths to allow for alernative input directories for unit tests
    path('<str:test_status>', import_acks, name='index'),
    path('acknowledge-samples/<str:gel1004>/<str:rack>/<str:test_status>', views.acknowledge_samples, name='acknowledge_samples'),
    path('problem-samples/<str:holding_rack_id>/<str:test_status>', views.problem_samples, name='problem_samples'),
    path('plate-holding-rack/<str:holding_rack_pk>/<str:test_status>', views.plate_holding_rack, name='plate_holding_rack'),
    path('ready-to-dispatch/<str:test_status>', views.ready_to_dispatch, name='ready_to_dispatch'),
]