from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
	path('register/', views.register, name='register'),
	path('login/', views.login_user, name='login'),
	path('logout/', views.logout_user, name='logout'),
	path('profile/', views.profile, name='profile'),
	path('add-chart-viewer/', views.add_admin, name='add_admin'),
	path('<int:pk>/remove-chart-viewer/', views.remove_admin, name='remove_admin'),
]

