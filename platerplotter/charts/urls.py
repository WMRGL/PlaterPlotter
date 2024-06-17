from django.urls import path

from . import views

app_name = 'charts'
urlpatterns = [
    path('cancer-rd/', views.CancerRareDiseaseView.as_view(), name='cancer_rd'),
    path('kpi/', views.KpiView.as_view(), name='kpi'),
]
