from django.urls import path

from . import views

app_name = 'charts'
urlpatterns = [
    path('cancer-rd/', views.CancerRareDiseaseView.as_view(), name='cancer_rd'),
    path('monthly-kpi/', views.MonthlyKpiView.as_view(), name='kpi'),
    path('month-total/', views.MonthTotalView.as_view(), name='month_total'),
    path('week-total/', views.WeekTotalView.as_view(), name='week_total'),
]
