
from decimal import Decimal, InvalidOperation


def get_cart(request):
    return request.session.get("cart", {})


def save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


def calculate_cart_total(cart):
    total = Decimal("0.00")

    for item in cart.values():
        try:
            price = Decimal(str(item.get("price", "0")))
            quantity = int(item.get("quantity", 0))

            if price >= 0 and quantity > 0:
                total += price * quantity

        except (InvalidOperation, ValueError, TypeError):
            continue

    return total.quantize(Decimal("0.01"))
