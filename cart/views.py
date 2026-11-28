
"""Views for the VELORA shopping cart and checkout."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from store.models import Product
from .cart_logic import get_cart, save_cart, calculate_cart_total


def prepare_cart(cart):
    """Prepare cart items using current product information from the database."""

    prepared_cart = {}

    if not isinstance(cart, dict):
        return prepared_cart

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(
                pk=int(product_id),
                is_available=True,
            )

            if not isinstance(item, dict):
                continue

            quantity = int(item.get("quantity", 1))

            if quantity < 1:
                continue

            price = product.price

            prepared_cart[str(product.id)] = {
                "name": product.name,
                "price": price,
                "image": product.image_url,
                "quantity": quantity,
                "subtotal": price * quantity,
                "available_stock": product.stock,
                "stock_limit_exceeded": (
                    quantity > product.stock or product.stock < 1
                ),
            }

        except (Product.DoesNotExist, ValueError, TypeError, AttributeError):
            continue

    return prepared_cart


def add_to_cart(request, product_id):
    """Add an available store product to the shopping cart."""

    if request.method != "POST":
        return redirect("home")

    product = get_object_or_404(
        Product,
        pk=product_id,
        is_available=True,
    )

    if product.stock < 1:
        messages.error(request, "This product is currently out of stock.")
        return redirect("home")

    cart = get_cart(request)

    if not isinstance(cart, dict):
        cart = {}

    product_id = str(product.id)

    try:
        current_quantity = int(
            cart.get(product_id, {}).get("quantity", 0)
        )
    except (AttributeError, TypeError, ValueError):
        current_quantity = 0

    if current_quantity >= product.stock:
        messages.warning(
            request,
            "Sorry, the available stock limit has been reached.",
        )
    else:
        cart[product_id] = {
            "quantity": current_quantity + 1,
        }

        save_cart(request, cart)

        messages.success(request, "Product added to your cart!")

    return redirect("cart:cart")


def cart_view(request):
    """Display the shopping cart."""

    cart = prepare_cart(get_cart(request))
    total = calculate_cart_total(cart)

    return render(request, "cart/cart.html", {
        "cart": cart,
        "total": total,
    })


def update_quantity(request, product_id):
    """Update the quantity of a cart product."""

    if request.method != "POST":
        return redirect("cart:cart")

    cart = get_cart(request)

    if not isinstance(cart, dict):
        cart = {}

    product_id = str(product_id)

    if product_id not in cart:
        messages.error(request, "Product not found in your cart.")
        return redirect("cart:cart")

    try:
        quantity = int(request.POST.get("quantity", 1))

        product = Product.objects.get(
            pk=int(product_id),
            is_available=True,
        )

        if quantity < 1:
            messages.error(request, "Quantity must be at least 1.")

        elif quantity > product.stock:
            messages.error(
                request,
                f"Only {product.stock} items are available.",
            )

        else:
            cart[product_id]["quantity"] = quantity
            save_cart(request, cart)

            messages.success(request, "Cart quantity updated.")

    except (ValueError, TypeError, Product.DoesNotExist, AttributeError):
        messages.error(
            request,
            "Unable to update this product quantity.",
        )

    return redirect("cart:cart")


def remove_from_cart(request, product_id):
    """Remove a product from the shopping cart."""

    if request.method != "POST":
        return redirect("cart:cart")

    cart = get_cart(request)

    if not isinstance(cart, dict):
        cart = {}

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]
        save_cart(request, cart)

        messages.success(request, "Product removed from your cart.")
    else:
        messages.error(request, "Product not found in your cart.")

    return redirect("cart:cart")


def checkout_view(request):
    """Collect and save customer delivery details."""

    cart = prepare_cart(get_cart(request))

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("cart:cart")

    total = calculate_cart_total(cart)
    checkout_details = request.session.get("checkout_details", {})

    if request.method == "POST":

        # Recheck stock before saving delivery details.
        if any(item["stock_limit_exceeded"] for item in cart.values()):
            messages.error(
                request,
                "Please update your cart because some products exceed available stock.",
            )

        else:
            full_name = request.POST.get("full_name", "").strip()
            phone = request.POST.get("phone", "").strip()
            address = request.POST.get("address", "").strip()
            city = request.POST.get("city", "").strip()

            phone_digits = "".join(
                character for character in phone if character.isdigit()
            )
            cleaned_phone = (
                phone.replace("+", "")
                .replace("-", "")
                .replace(" ", "")
                .replace("(", "")
                .replace(")", "")
            )

            if not all([full_name, phone, address, city]):
                messages.error(
                    request,
                    "Please fill in all delivery details.",
                )

            elif len(full_name) < 3:
                messages.error(
                    request,
                    "Please enter a valid full name.",
                )

            elif (
                not cleaned_phone.isdigit()
                or not 10 <= len(phone_digits) <= 13
            ):
                messages.error(
                    request,
                    "Please enter a valid phone number.",
                )

            elif len(address) < 5:
                messages.error(
                    request,
                    "Please enter a complete delivery address.",
                )

            else:
                request.session["checkout_details"] = {
                    "full_name": full_name,
                    "phone": phone,
                    "address": address,
                    "city": city,
                }

                # Store JSON-serializable values in the session.
                checkout_items = {
                    product_id: {
                        "name": item["name"],
                        "price": str(item["price"]),
                        "quantity": item["quantity"],
                        "subtotal": str(item["subtotal"]),
                    }
                    for product_id, item in cart.items()
                }

                request.session["checkout_summary"] = {
                    "items": checkout_items,
                    "total": str(total),
                    "status": "delivery_details_saved",
                }

                request.session.modified = True

                messages.success(
                    request,
                    "Delivery details saved successfully.",
                )

                return redirect("cart:checkout")

    return render(request, "cart/checkout.html", {
        "cart": cart,
        "total": total,
        "checkout_details": checkout_details,
    })
