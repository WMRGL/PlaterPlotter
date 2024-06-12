from django.urls import path

from . import views

app_name = 'charts'
urlpatterns = [
    path('', views.ChartsView.as_view(), name='index'),
    path('kpi/', views.KpiView.as_view(), name='kpi'),
]