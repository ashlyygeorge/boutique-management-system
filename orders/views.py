from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import razorpay

from cart.models import cartdetails
from store.models import productdetails
from .models import orderdetails, orderitems


def checkout(request):

    if "uname" not in request.session:
        return redirect("login")

    username = request.session["uname"]

    cart_items = cartdetails.objects.filter(username=username)

    if not cart_items:
        return redirect("cart")

    total = 0
    out_of_stock = False
    unavailable_product = False

    # ================= CHECK CART PRODUCTS =================

    for item in cart_items:

        try:
            item.product = productdetails.objects.get(
                id=item.productid
            )

        except productdetails.DoesNotExist:

            unavailable_product = True
            out_of_stock = True
            item.product = None
            item.item_total = 0
            continue

        if (
            not item.product.status
            or item.product.stock < item.quantity
        ):
            out_of_stock = True

        item.item_total = (
            item.product.product_price * item.quantity
        )

        total += item.item_total

    # ================= PLACE ORDER =================

    if request.method == "POST":

        for item in cart_items:

            try:
                product = productdetails.objects.get(
                    id=item.productid
                )

            except productdetails.DoesNotExist:

                return render(request, "checkout.html", {
                    "cart_items": cart_items,
                    "total": total,
                    "out_of_stock": True,
                    "unavailable_product": True
                })

            if (
                not product.status
                or product.stock < item.quantity
            ):

                return render(request, "checkout.html", {
                    "cart_items": cart_items,
                    "total": total,
                    "out_of_stock": True
                })

        # ================= CUSTOMER DETAILS =================

        customer_name = request.POST.get("fullname")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        payment_method = request.POST.get(
            "payment_method",
            "Cash on Delivery"
        )

        # =====================================================
        # CASH ON DELIVERY
        # =====================================================

        if payment_method == "Cash on Delivery":

            order = orderdetails.objects.create(
                customer=username,
                customer_name=customer_name,
                phone=phone,
                address=address,
                total_amount=total,
                payment_method="Cash on Delivery",
                order_status="Pending"
            )

            for item in cart_items:

                product = productdetails.objects.get(
                    id=item.productid
                )

                orderitems.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=product.product_price
                )

                product.stock -= item.quantity

                if product.stock == 0:
                    product.status = False

                product.save()

            cart_items.delete()

            return redirect("order_success")

        # =====================================================
        # RAZORPAY
        # =====================================================

        if payment_method == "Razorpay":

            client = razorpay.Client(
                auth=(
                    settings.RAZORPAY_KEY_ID,
                    settings.RAZORPAY_KEY_SECRET
                )
            )

            # Convert rupees to paise
            amount = int(total * 100)

            razorpay_order = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": 1
            })

            order = orderdetails.objects.create(
                customer=username,
                customer_name=customer_name,
                phone=phone,
                address=address,
                total_amount=total,
                payment_method="Razorpay",
                razorpay_order_id=razorpay_order["id"],
                order_status="Pending"
            )

            request.session["pending_order_id"] = order.id

            return render(request, "payment.html", {
                "key": settings.RAZORPAY_KEY_ID,
                "amount": amount,
                "total": total,
                "order_id": razorpay_order["id"],
                "customer_name": customer_name,
                "phone": phone,
                "email": request.session.get(
                    "useremail",
                    ""
                )
            })

    # ================= SHOW CHECKOUT =================

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total": total,
        "out_of_stock": out_of_stock,
        "unavailable_product": unavailable_product
    })


# =========================================================
# RAZORPAY PAYMENT SUCCESS
# =========================================================

@csrf_exempt
def payment_success(request):

    if request.method != "POST":
        return redirect("checkout")

    payment_id = request.POST.get(
        "razorpay_payment_id"
    )

    razorpay_order_id = request.POST.get(
        "razorpay_order_id"
    )

    signature = request.POST.get(
        "razorpay_signature"
    )

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    # ================= VERIFY PAYMENT =================

    try:

        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        })

    except razorpay.errors.SignatureVerificationError:

        return render(
            request,
            "payment_failed.html"
        )

    # ================= FIND ORDER =================

    try:

        order = orderdetails.objects.get(
            razorpay_order_id=razorpay_order_id
        )

    except orderdetails.DoesNotExist:

        return render(
            request,
            "payment_failed.html"
        )

    # ================= PREVENT DUPLICATE PAYMENT =================

    if order.razorpay_payment_id:

        return redirect("order_success")

    # ================= SAVE PAYMENT =================

    order.razorpay_payment_id = payment_id
    order.order_status = "Confirmed"
    order.save()

    # ================= GET CART =================

    username = order.customer

    cart_items = cartdetails.objects.filter(
        username=username
    )

    # ================= SAVE ORDER ITEMS =================

    for item in cart_items:

        try:

            product = productdetails.objects.get(
                id=item.productid
            )

        except productdetails.DoesNotExist:

            continue

        orderitems.objects.create(
            order=order,
            product=product,
            quantity=item.quantity,
            price=product.product_price
        )

        # Reduce stock only after successful payment
        product.stock -= item.quantity

        if product.stock == 0:
            product.status = False

        product.save()

    # ================= REMOVE CART ITEMS =================

    cart_items.delete()

    request.session.pop(
        "pending_order_id",
        None
    )

    return redirect("order_success")


# =========================================================
# ORDER SUCCESS
# =========================================================

def order_success(request):

    return render(
        request,
        "order_success.html"
    )


# =========================================================
# ORDER HISTORY
# =========================================================

def order_history(request):

    if "uname" not in request.session:
        return redirect("login")

    username = request.session["uname"]

    orders = orderdetails.objects.filter(
        customer=username
    ).order_by("-order_date")

    return render(request, "order_history.html", {
        "orders": orders
    })


# =========================================================
# ORDER DETAILS
# =========================================================

def order_details(request, id):

    if "uname" not in request.session:
        return redirect("login")

    username = request.session["uname"]

    order = orderdetails.objects.get(
        id=id,
        customer=username
    )

    return render(request, "order_details.html", {
        "order": order
    })


# =========================================================
# ADMIN ORDERS
# =========================================================

def admin_orders(request):

    if "admin" not in request.session:
        return redirect("login")

    orders = orderdetails.objects.all().order_by(
        "-order_date"
    )

    for order in orders:

        for item in order.orderitems_set.all():

            item.item_total = (
                item.price * item.quantity
            )

    return render(request, "admin_orders.html", {
        "orders": orders
    })


# =========================================================
# UPDATE ORDER STATUS
# =========================================================

def update_order_status(request, id):

    if "admin" not in request.session:
        return redirect("login")

    order = orderdetails.objects.get(
        id=id
    )

    if request.method == "POST":

        new_status = request.POST.get(
            "status"
        )

        # Return stock when order is cancelled
        # for the first time.
        if (
            new_status == "Cancelled"
            and order.order_status != "Cancelled"
        ):

            for item in order.orderitems_set.all():

                product = item.product

                product.stock += item.quantity

                if product.stock > 0:
                    product.status = True

                product.save()

        order.order_status = new_status
        order.save()

    return redirect("admin_orders")


# =========================================================
# CUSTOMER CANCEL ORDER
# =========================================================

def cancel_order(request, id):

    if "uname" not in request.session:
        return redirect("login")

    username = request.session["uname"]

    order = orderdetails.objects.get(
        id=id,
        customer=username
    )

    # Customer can cancel only Pending or Confirmed orders
    if order.order_status not in [
        "Pending",
        "Confirmed"
    ]:

        return redirect(
            "order_details",
            id=id
        )

    # Restore stock
    for item in order.orderitems_set.all():

        product = item.product

        product.stock += item.quantity

        if product.stock > 0:
            product.status = True

        product.save()

    # Change order status
    order.order_status = "Cancelled"
    order.save()

    return redirect(
        "order_details",
        id=id
    )