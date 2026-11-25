
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect
from django.contrib import messages

from .cart_logic import get_cart, save_cart, calculate_cart_total


# Temporary products until Sprint 1 Product model is integrated
SAMPLE_PRODUCTS = {
    "1": {
        "name": "Sample Product 1",
        "price": "1500.00",
        "image": "",
    },
    "2": {
        "name": "Sample Product 2",
        "price": "2500.00",
        "image": "",
    },
}


def prepare_cart(cart):
    """Prepare cart items with individual subtotals."""

    prepared_cart = {}

    for product_id, item in cart.items():
        try:
            price = Decimal(str(item["price"]))
            quantity = int(item["quantity"])

            if price < 0 or quantity <= 0:
                continue

            prepared_cart[product_id] = {
                **item,
                "price": price,
                "quantity": quantity,
                "subtotal": price * quantity,
            }

        except (KeyError, ValueError, TypeError, InvalidOperation):
            continue

    return prepared_cart


# Add product to cart
def add_to_cart(request, product_id):

    if request.method != "POST":
        return redirect("cart:cart")

    product_id = str(product_id)
    product = SAMPLE_PRODUCTS.get(product_id)

    if not product:
        messages.error(request, "Product not found.")
        return redirect("cart:cart")

    cart = get_cart(request)

    if product_id in cart:
        cart[product_id]["quantity"] += 1

    else:
        cart[product_id] = {
            "name": product["name"],
            "price": product["price"],
            "image": product["image"],
            "quantity": 1,
        }

    save_cart(request, cart)

    messages.success(request, "Product added to cart!")

    return redirect("cart:cart")


# Display cart page
def cart_view(request):

    cart = prepare_cart(get_cart(request))
    total = calculate_cart_total(cart)

    return render(request, "cart/cart.html", {
        "cart": cart,
        "total": total,
    })


# Update product quantity
def update_quantity(request, product_id):

    if request.method == "POST":

        cart = get_cart(request)
        product_id = str(product_id)

        if product_id in cart:

            try:
                quantity = int(request.POST.get("quantity", 1))

                if quantity < 1:
                    messages.error(request, "Quantity must be at least 1.")

                else:
                    cart[product_id]["quantity"] = quantity
                    save_cart(request, cart)
                    messages.success(request, "Cart quantity updated.")

            except (ValueError, TypeError):
                messages.error(request, "Please enter a valid quantity.")

    return redirect("cart:cart")


# Remove product from cart
def remove_from_cart(request, product_id):

    if request.method == "POST":

        cart = get_cart(request)
        product_id = str(product_id)

        if product_id in cart:
            del cart[product_id]
            save_cart(request, cart)

            messages.success(request, "Product removed from cart.")

    return redirect("cart:cart")


# Checkout and delivery details
def checkout_view(request):

    cart = prepare_cart(get_cart(request))

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("cart:cart")

    total = calculate_cart_total(cart)

    checkout_details = request.session.get("checkout_details", {})

    if request.method == "POST":

        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()

        phone_digits = "".join(
            character for character in phone if character.isdigit()
        )

        if not all([full_name, phone, address, city]):

            messages.error(request, "Please fill in all delivery details.")

        elif len(full_name) < 3:

            messages.error(request, "Please enter a valid full name.")

        elif not phone.replace("+", "").replace("-", "").replace(" ", "").isdigit() or not 10 <= len(phone_digits) <= 13:

            messages.error(request, "Please enter a valid phone number.")

        elif len(address) < 5:

            messages.error(request, "Please enter a complete delivery address.")

        else:

            request.session["checkout_details"] = {
                "full_name": full_name,
                "phone": phone,
                "address": address,
                "city": city,
            }

            request.session["checkout_summary"] = {
                "items": cart,
                "total": str(total),
                "status": "delivery_details_saved",
            }

            request.session.modified = True

            messages.success(
                request,
                "Delivery details saved successfully."
            )

            return redirect("cart:checkout")

    return render(request, "cart/checkout.html", {
        "cart": cart,
        "total": total,
        "checkout_details": checkout_details,
    })
