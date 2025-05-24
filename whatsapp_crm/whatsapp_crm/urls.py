"""
URL configuration for whatsapp_crm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include # Added include

from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), # Standard auth URLs
    path('clients/', include('clients.urls', namespace='clients')),
    # Redirect root to login page if not authenticated, or home if authenticated.
    # For now, let's keep it simple and redirect to login, home.html will handle authenticated users.
    # A more complex setup might involve a dedicated landing page.
    path('', RedirectView.as_view(pattern_name='login', permanent=False)),
    # The users app urls are now effectively handled by django.contrib.auth.urls
    # or will be if we add specific user profile views later under 'accounts/' or a new path.
    # path('users/', include('users.urls')), # Removed for now
]
