from django.urls import path

from . import views

app_name = 'charts'
urlpatterns = [
    path('cancer-rd/', views.CancerRareDiseaseView.as_view(), name='cancer_rd'),
    path('kpi/', views.KpiView.as_view(), name='kpi'),
    path('month-total/', views.MonthTotalView.as_view(), name='month_total'),
]
