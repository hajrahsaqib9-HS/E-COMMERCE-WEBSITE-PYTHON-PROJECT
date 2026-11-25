
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [

    # Display shopping cart
    path('', views.cart_view, name='cart'),

    # Add product to cart
    path('add/<str:product_id>/', views.add_to_cart, name='add_to_cart'),

    # Update product quantity
    path('update/<str:product_id>/', views.update_quantity, name='update_quantity'),

    # Remove product from cart
    path('remove/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Checkout page
    path('checkout/', views.checkout_view, name='checkout'),

]
