
"""Admin configuration for the store app."""

from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Customize product management in Django admin."""

    list_display = (
        'name',
        'category',
        'price',
        'stock',
        'is_available',
        'is_featured',
    )

    list_filter = ('category', 'is_available', 'is_featured')

    search_fields = ('name', 'category')

    list_editable = ('price', 'stock', 'is_available', 'is_featured')
