from django.urls import path

from . import views

urlpatterns = [
    path("place/", views.place_order, name="place_order"),
    path("confirmation/<uuid:order_number>/", views.order_confirmation, name="order_confirmation"),
    path("history/", views.order_history, name="order_history"),
    path("<uuid:order_number>/", views.order_details, name="order_details"),
]
