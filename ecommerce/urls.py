"""
URL configuration for the ecommerce project.
"""

from django.contrib import admin
from django.urls import path, include
from store.views import home

urlpatterns = [
    path('admin/', admin.site.urls),

    # E-commerce homepage
    path('', home, name='home'),

    # Hareem's Authentication & Account module
    path('accounts/', include('accounts.urls')),
]