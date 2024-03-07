from django.urls import path

from . import views
from problemsamples import views as problems

app_name = 'awaitingsorting'

urlpatterns = [
    path('holding-rack-assignment/', views.awaiting_holding_rack_assignment, name='awaiting_holding_rack_assignment'),
    path('assign-samples-to-holding-rack/<str:gel1004>/<str:rack>', views.assign_samples_to_holding_rack,
         name='assign_samples_to_holding_rack'),
    path('assign-samples-to-holding-rack/<str:gel1004>/<str:rack>/<str:holding_rack_id>',
         views.assign_samples_to_holding_rack, name='assign_samples_to_holding_rack'),
    path('assign-samples-to-holding-rack/<str:rack>', views.assign_samples_to_holding_rack,
         name='assign_samples_to_holding_rack'),
    path('assign-problem-rack-samples-to-holding-rack/<str:rack>/<str:holding_rack_id>',
         views.assign_samples_to_holding_rack, name='assign_problem_samples_to_holding_rack'),
    path('delete-sample/<str:gel1004>/<str:rack>/<str:holding_rack_id>/<str:sample_id>/', views.delete_sample,
         name='delete_sample'),
]
