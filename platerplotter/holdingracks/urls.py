from django.urls import path

from . import views

app_name = 'holdingracks'

urlpatterns = [
    path('racks/', views.holding_racks, name='holding_racks'),
    path('racks/<str:holding_rack_id>', views.holding_racks, name='holding_racks'),
    path('racks/<str:holding_rack_id>/<str:holding_racks_well_id>/', views.holding_racks_well,
         name='holding_racks_well'),
    path('plate-holding-rack/<str:holding_rack_pk>', views.plate_holding_rack, name='plate_holding_rack'),
    path('delete-sample/<str:gel1004>/<str:rack>/<str:holding_rack_id>/<str:sample_id>/', views.delete_sample,
         name='delete_sample'),
    # test
    path('plate-holding-rack/<str:holding_rack_pk>/<str:test_status>', views.plate_holding_rack,
         name='plate_holding_rack'),

]
