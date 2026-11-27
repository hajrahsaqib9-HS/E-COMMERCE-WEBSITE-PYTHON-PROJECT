"""
URL configuration for the ecommerce project.
"""

from django.contrib import admin
from django.urls import path, include
from store.views import home

urlpatterns = [
    path('admin/', admin.site.urls),

    # Homepage and product browsing
    path('', home, name='home'),

    # Authentication and accounts
    path('accounts/', include('accounts.urls')),

    # Order management
    path('orders/', include('orders.urls')),
]
