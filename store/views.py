
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import productdetails, Wishlist
from orders.models import orderitems


def add_product(request):

    if "admin" not in request.session:
        return redirect("login")

    if request.method == "POST":

        product_name = request.POST.get("product_name")
        product_category = request.POST.get("product_category")
        product_price = request.POST.get("product_price")
        product_description = request.POST.get("product_description")
        product_image = request.FILES.get("product_image")
        stock = request.POST.get("stock")
        status = request.POST.get("status")

        available_sizes = request.POST.getlist("sizes")

        product = productdetails(
            product_name=product_name,
            product_category=product_category,
            product_price=product_price,
            product_description=product_description,
            product_image=product_image,
            stock=stock,
            status=True if status == "on" else False,
            available_sizes=available_sizes
        )

        product.save()

        return redirect("add_product")

    return render(request, "add_product.html")


def product_list(request):

    search = request.GET.get("search")
    category = request.GET.get("category")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    sort = request.GET.get("sort")

    products = productdetails.objects.all()

    if search:
        products = products.filter(
            product_name__icontains=search
        )

    if category:
        if category == "Others":
            products = products.exclude(
                product_category__in=["Dresses", "Kurti"]
            )
        else:
            products = products.filter(
                product_category=category
            )

    if min_price:
        products = products.filter(
            product_price__gte=min_price
        )

    if max_price:
        products = products.filter(
            product_price__lte=max_price
        )

    if sort == "price_low":
        products = products.order_by("product_price")
    elif sort == "price_high":
        products = products.order_by("-product_price")
    elif sort == "name_az":
        products = products.order_by("product_name")
    elif sort == "name_za":
        products = products.order_by("-product_name")

    categories = productdetails.objects.values_list(
        "product_category",
        flat=True
    ).distinct()

    for product in products:
        product.order_count = orderitems.objects.filter(
            product=product
        ).count()

    wishlist_ids = []

    if "uid" in request.session:
        wishlist_ids = Wishlist.objects.filter(
            user_id=request.session["uid"]
        ).values_list(
            "product_id",
            flat=True
        )

    return render(
        request,
        "product_list.html",
        {
            "products": products,
            "categories": categories,
            "wishlist_ids": wishlist_ids
        }
    )


def product_details(request, id):
    product = productdetails.objects.get(id=id)

    in_wishlist = False

    if request.session.get("user") == "user":
        in_wishlist = Wishlist.objects.filter(
            user_id=request.session["uid"],
            product_id=product.id
        ).exists()

    return render(request, 'product.html', {
        'product': product,
        'in_wishlist': in_wishlist
    })


def update_product(request, id):

    if "admin" not in request.session:
        return redirect("login")

    product = productdetails.objects.get(id=id)

    if request.method == "POST":

        product.product_name = request.POST.get("product_name")
        product.product_category = request.POST.get("product_category")
        product.product_price = request.POST.get("product_price")
        product.product_description = request.POST.get(
            "product_description"
        )

        product.stock = int(
            request.POST.get("stock", 0)
        )

        status = request.POST.get("status")
        product.status = True if status == "True" else False

        product.available_sizes = request.POST.getlist("sizes")

        if request.FILES.get("product_image"):
            product.product_image = request.FILES.get(
                "product_image"
            )

        product.save()

        return redirect(
            "product_details",
            id=product.id
        )

    return render(
        request,
        "update_product.html",
        {
            "product": product
        }
    )


def remove_stock(request, id):

    if "admin" not in request.session:
        return redirect("login")

    product = productdetails.objects.get(id=id)

    if request.method == "POST":

        quantity = int(
            request.POST.get("quantity", 0)
        )

        if quantity > 0 and quantity <= product.stock:

            product.stock -= quantity

            if product.stock == 0:
                product.status = False

            product.save()

        return redirect("product_list")

    quantities = range(
        1,
        product.stock + 1
    )

    return render(
        request,
        "remove_stock.html",
        {
            "product": product,
            "quantities": quantities
        }
    )


def delete_product(request, id):

    if "admin" not in request.session:
        return redirect("login")

    product = productdetails.objects.get(id=id)

    order_count = orderitems.objects.filter(
        product=product
    ).count()

    if request.method == "POST":

        if order_count > 0:

            messages.error(
                request,
                "This product has already been ordered and cannot be deleted."
            )

            return redirect("product_list")

        product.delete()

        messages.success(
            request,
            "Product deleted successfully."
        )

        return redirect("product_list")

    return render(
        request,
        "delete_product.html",
        {
            "product": product,
            "order_count": order_count
        }
    )


def add_to_wishlist(request, product_id):

    if "uid" not in request.session:
        return redirect("login")

    product = productdetails.objects.get(
        id=product_id
    )

    Wishlist.objects.get_or_create(
        user_id=request.session["uid"],
        product=product
    )

    next_url = request.GET.get("next")

    if next_url and next_url.startswith("/"):
        return redirect(next_url)

    return redirect("index")


def remove_from_wishlist(request, product_id):

    if "uid" not in request.session:
        return redirect("login")

    Wishlist.objects.filter(
        user_id=request.session["uid"],
        product_id=product_id
    ).delete()

    next_url = request.GET.get("next")

    if next_url and next_url.startswith("/"):
        return redirect(next_url)

    return redirect("index")


def wishlist(request):

    if "uid" not in request.session:
        return redirect("login")

    wishlist_items = Wishlist.objects.filter(
        user_id=request.session["uid"]
    ).select_related("product")

    return render(
        request,
        "wishlist.html",
        {
            "wishlist_items": wishlist_items
        }
    )
