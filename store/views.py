
"""Views for the VELORA store."""

from django.shortcuts import render
from .models import Product
from cart.cart_logic import get_cart

# pylint: disable=no-member


def home(request):
    """Display homepage and filter products by category."""

    selected_category = request.GET.get('category', '').strip()

    if selected_category:
        products = Product.objects.filter(
            is_available=True,
            category__iexact=selected_category
        )
    else:
        products = Product.objects.filter(
            is_available=True,
            is_featured=True
        )

    categories = Product.objects.filter(
        is_available=True
    ).values_list('category', flat=True).distinct()

    # Calculate total quantity of products in the session cart.
    session_cart = get_cart(request)
    cart_count = 0

    if isinstance(session_cart, dict):
        for item in session_cart.values():
            if isinstance(item, dict):
                try:
                    quantity = int(item.get('quantity', 0))
                    if quantity > 0:
                        cart_count += quantity
                except (ValueError, TypeError):
                    continue

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'cart_count': cart_count,
    }

    return render(request, 'home.html', context)
