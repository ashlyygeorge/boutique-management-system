from django.shortcuts import render, redirect
from .models import cartdetails
from store.models import productdetails
from django.contrib import messages

def add_to_cart(request, id):

    if "uname" not in request.session:
        messages.error(request, "Please login to add products to cart.")
        return redirect("login")

    username = request.session["uname"]

    product = productdetails.objects.get(id=id)

    # Check product availability
    if product.stock <= 0 or not product.status:
        return redirect("product_list")

    # Check if product is already in cart
    cart_item = cartdetails.objects.filter(
        username=username,
        productid=product.id
    ).first()

    if cart_item:

        # Don't allow quantity to exceed stock
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()

    else:

        cart_item = cartdetails(
            username=username,
            productname=product.product_name,
            productid=product.id,
            productprice=product.product_price,
            quantity=1
        )

        cart_item.save()

    return redirect("cart")

def cart(request):

    if "uname" not in request.session:
        return redirect("login")

    username = request.session["uname"]

    cart_items = cartdetails.objects.filter(username=username)

    total = 0

    for item in cart_items:

        try:
            item.product = productdetails.objects.get(
                id=item.productid
            )

            item.item_total = item.product.product_price * item.quantity
            total += item.item_total

        except productdetails.DoesNotExist:

            item.product = None
            item.item_total = 0

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total
    })

def remove_item(request, id):

    if "uname" not in request.session:
        return redirect("login")

    username = request.session["uname"]

    cart_item = cartdetails.objects.get(
        id=id,
        username=username
    )

    cart_item.delete()

    return redirect("cart")



def update_quantity(request, id):

    if "uname" not in request.session:
        return redirect("login")

    username = request.session["uname"]

    cart_item = cartdetails.objects.get(
        id=id,
        username=username
    )

    # Get the current product
    try:
        product = productdetails.objects.get(
            id=cart_item.productid
        )
    except productdetails.DoesNotExist:
        return redirect("cart")

    # Get requested quantity
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (ValueError, TypeError):
        quantity = 1

    # Quantity must be at least 1
    if quantity < 1:
        quantity = 1

    # Quantity cannot be greater than current stock
    if quantity > product.stock:
        messages.error(
            request,
            f"Only {product.stock} item(s) of {product.product_name} are currently available."
        )
        return redirect("cart")

    # Product must still be active
    if not product.status:
        messages.error(
            request,
            f"{product.product_name} is currently out of stock."
        )
        return redirect("cart")

    cart_item.quantity = quantity
    cart_item.save()

    return redirect("cart")