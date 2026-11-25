"""URL configuration for the VELORA e-commerce project."""

from django.contrib import admin
from django.urls import path, include
from store.views import home

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home and Product Browsing - Hajrah
    path('', home, name='home'),

    # Authentication and Account - Hareem
    path('accounts/', include('accounts.urls')),

    # Cart and Checkout - Rida
    path('cart/', include('cart.urls')),
]
