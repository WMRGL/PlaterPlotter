from django.urls import path

from . import views


app_name = 'notifications'

urlpatterns = [
	path('<str:test_status>', views.import_acks, name='index'),

]
