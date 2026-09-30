
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import userdetails
from store.models import productdetails, Wishlist
from orders.models import orderdetails, orderitems


# =========================================================
# REGISTER
# =========================================================

def register(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        useremail = request.POST.get("useremail", "").strip().lower()
        userphone = request.POST.get("userphone", "").strip()
        userpassword = request.POST.get("userpassword", "")

        # Check empty fields
        if not username or not useremail or not userphone or not userpassword:

            return render(
                request,
                "register.html",
                {
                    "msg": "Please fill in all fields."
                }
            )

        # Validate email
        try:
            validate_email(useremail)

        except ValidationError:

            return render(
                request,
                "register.html",
                {
                    "msg": "Please enter a valid email address."
                }
            )

        # Check phone number
        if (
            not userphone.isdigit()
            or len(userphone) != 10
            or userphone[0] not in "6789"
        ):

            return render(
                request,
                "register.html",
                {
                    "msg": "Please enter a valid Indian mobile number."
                }
            )

        # Check duplicate email
        if userdetails.objects.filter(
            useremail=useremail
        ).exists():

            return render(
                request,
                "register.html",
                {
                    "msg": "Email is already registered."
                }
            )

        # Check duplicate phone
        if userdetails.objects.filter(
            userphone=userphone
        ).exists():

            return render(
                request,
                "register.html",
                {
                    "msg": "Phone number is already registered."
                }
            )

        # Check password length
        if len(userpassword) < 6:

            return render(
                request,
                "register.html",
                {
                    "msg": "Password must contain at least 6 characters."
                }
            )

        # Create customer
        data = userdetails(
            username=username,
            useremail=useremail,
            userphone=userphone,
            userpassword=userpassword
        )

        data.save()

        messages.success(
            request,
            "Account created successfully. Please login."
        )

        return redirect("login")

    return render(request, "register.html")


# =========================================================
# LOGIN
# =========================================================

def login(request):

    if request.method == "POST":

        useremail = request.POST.get(
            "useremail",
            ""
        ).strip().lower()

        userpassword = request.POST.get(
            "userpassword",
            ""
        )

        # Check empty fields
        if not useremail or not userpassword:

            return render(
                request,
                "login.html",
                {
                    "msg": "Please enter your email and password."
                }
            )

        # ADMIN LOGIN
        if (
            useremail == "admin@gmail.com"
            and userpassword == "admin"
        ):

            request.session.flush()

            request.session["admin"] = "admin"
            request.session["uid"] = 0
            request.session["uname"] = "Administrator"
            request.session["useremail"] = useremail

            return redirect("index")

        # CUSTOMER LOGIN
        user = userdetails.objects.filter(
            useremail=useremail
        ).first()

        if user is None:

            return render(
                request,
                "login.html",
                {
                    "msg": "Email is not registered."
                }
            )

        # Password check
        if userpassword != user.userpassword:

            return render(
                request,
                "login.html",
                {
                    "msg": "Incorrect password."
                }
            )

        # CUSTOMER SESSION
        request.session.flush()

        request.session["uid"] = user.id
        request.session["uname"] = user.username
        request.session["useremail"] = user.useremail
        request.session["user"] = "user"

        return redirect("index")

    return render(request, "login.html")


# =========================================================
# USER VIEW
# =========================================================

def userview(request):

    if "admin" not in request.session:
        return redirect("login")

    user_data = userdetails.objects.all()

    return render(
        request,
        "userview.html",
        {
            "result": user_data
        }
    )


# =========================================================
# DELETE USER
# =========================================================

def delete_user(request, id):

    if "admin" not in request.session:
        return redirect("login")

    try:

        user = userdetails.objects.get(
            id=id
        )

    except userdetails.DoesNotExist:

        messages.error(
            request,
            "Customer not found."
        )

        return redirect("userview")

    # Check if customer has orders
    has_orders = orderdetails.objects.filter(
        customer=user.username
    ).exists()

    if has_orders:

        messages.error(
            request,
            "This customer cannot be deleted because they have existing orders."
        )

        return redirect("userview")

    user.delete()

    messages.success(
        request,
        "Customer deleted successfully."
    )

    return redirect("userview")


# =========================================================
# LOGOUT
# =========================================================

def logout(request):

    request.session.flush()

    return redirect("index")


# =========================================================
# PROFILE
# =========================================================

def profile(request):

    if "uid" not in request.session:
        return redirect("login")

    uid = request.session["uid"]

    try:

        user = userdetails.objects.get(
            id=uid
        )

    except userdetails.DoesNotExist:

        request.session.flush()

        return redirect("login")

    return render(
        request,
        "profile.html",
        {
            "user": user
        }
    )


# =========================================================
# HOME / INDEX
# =========================================================

def index(request):

    all_products = productdetails.objects.all().order_by("-id")

    # Latest products shown in Latest Boutique Arrivals
    latest_products = all_products[:6]

    # Products shown in collection section
    collection_products = all_products[6:9]

    # -------------------------------------------------
    # WISHLIST
    # -------------------------------------------------

    wishlist_ids = set()

    if "uid" in request.session:

        wishlist_ids = set(
            Wishlist.objects.filter(
                user_id=request.session["uid"]
            ).values_list(
                "product_id",
                flat=True
            )
        )

    # -------------------------------------------------
    # BEST SELLING PRODUCTS
    # -------------------------------------------------

    # Products already displayed in other home sections
    home_product_ids = set(
        list(
            latest_products.values_list(
                "id",
                flat=True
            )
        )
        +
        list(
            collection_products.values_list(
                "id",
                flat=True
            )
        )
    )

    best_sellers = []

    for product in all_products:

        # Do not repeat products already shown above
        if product.id in home_product_ids:
            continue

        # Find all order items for this product
        # Cancelled orders are not counted
        sold_quantity = 0

        product_orders = orderitems.objects.filter(
            product=product
        ).exclude(
            order__order_status="Cancelled"
        )

        for item in product_orders:
            sold_quantity += item.quantity

        # Only products that have actually been ordered
        if sold_quantity > 0:

            product.sold_quantity = sold_quantity

            best_sellers.append(product)

    # Sort by highest quantity sold
    best_sellers.sort(
        key=lambda product: product.sold_quantity,
        reverse=True
    )

    # Show maximum 6 best-selling products
    best_sellers = best_sellers[:6]

    # -------------------------------------------------
    # RENDER HOME PAGE
    # -------------------------------------------------

    return render(
        request,
        "index.html",
        {
            "products": latest_products,
            "collection_products": collection_products,
            "wishlist_ids": wishlist_ids,
            "best_sellers": best_sellers
        }
    )

