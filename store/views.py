
"""Views for the VELORA store."""

from django.shortcuts import render
from .models import Product

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

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
    }

    return render(request, 'home.html', context)
