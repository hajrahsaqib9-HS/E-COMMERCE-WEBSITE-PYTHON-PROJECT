
"""Views for handling customer orders."""

# pylint: disable=no-member

from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Order, OrderItem


def place_order(request):
    """Creates a new customer order."""
    if request.method == "POST":
        name = request.POST.get("customer_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        payment = request.POST.get("payment_method", "").strip()
        product = request.POST.get("product_name", "").strip()

        try:
            quantity = int(request.POST.get("quantity", 1))
            price = Decimal(request.POST.get("price", "0"))
        except (ValueError, InvalidOperation):
            messages.error(request, "Quantity ya price galat hai.")
            return render(request, "orders/place_order.html")

        required = [name, email, phone, address, city, payment, product]

        if not all(required) or quantity < 1 or price <= 0:
            messages.error(
                request,
                "Barae meherbani saari details sahi bharein.",
            )
            return render(request, "orders/place_order.html")

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            payment_method=payment,
            total_amount=quantity * price,
        )

        OrderItem.objects.create(
            order=order,
            product_name=product,
            quantity=quantity,
            price=price,
        )

        return redirect(
            "order_confirmation",
            order_number=order.order_number,
        )

    return render(request, "orders/place_order.html")


def order_confirmation(request, order_number):
    """Displays the order confirmation page."""
    order = get_object_or_404(Order, order_number=order_number)
    return render(
        request,
        "orders/order_confirmation.html",
        {"order": order},
    )


@login_required
def order_history(request):
    """Displays the logged-in user's order history."""
    orders = Order.objects.filter(user=request.user)
    return render(
        request,
        "orders/order_history.html",
        {"orders": orders},
    )


def order_details(request, order_number):
    """Displays the details of a specific order."""
    order = get_object_or_404(Order, order_number=order_number)
    return render(
        request,
        "orders/order_details.html",
        {"order": order},
    )
