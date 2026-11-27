
"""Admin configuration for the orders app."""

from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Displays order items inside the order admin page."""

    model = OrderItem
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    """Configures the order admin interface."""

    list_display = (
        "short_number",
        "customer_name",
        "email",
        "total_amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("customer_name", "email", "order_number")
    inlines = [OrderItemInline]


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
