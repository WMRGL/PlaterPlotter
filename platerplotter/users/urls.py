from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
	path('register/', views.register, name='register'),
	path('login/', views.login_user, name='login'),
	path('logout/', views.logout_user, name='logout'),
	path('admin/', views.add_admin, name='add_admin'),
	path('<int:pk>/remove-admin/', views.remove_admin, name='remove_admin'),
]

