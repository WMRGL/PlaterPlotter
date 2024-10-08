"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


#from django.contrib.auth import views as auth_views
from notifications.views import import_acks

urlpatterns = [
    path(r'', include('platerplotter.urls')),
    # path('login/', auth_views.LoginView.as_view(template_name="registration/login.html"), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),
    path('notifications/', include('notifications.urls')),
    path('problem/', include('problemsamples.urls')),
    path('awaiting/', include('awaitingsorting.urls')),
    path('holding/', include('holdingracks.urls')),
    path('ready/', include('ready.urls')),
    path('discard/', include('discards.urls')),
    path('charts/', include('charts.urls')),
    path('users/', include('users.urls')),
    path('', import_acks, name='index'),
]

urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
