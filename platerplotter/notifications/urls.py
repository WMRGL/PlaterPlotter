from django.urls import path

from . import views


app_name = 'notifications'

urlpatterns = [
	path('<str:test_status>', views.import_acks, name='index'),
	path('post/ajax/volume', views.post_volume_check, name="post_volume_check"),

]
