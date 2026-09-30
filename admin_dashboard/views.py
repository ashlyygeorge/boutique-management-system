from django.shortcuts import render, redirect

from store.models import productdetails, Wishlist
from accounts.models import userdetails
from orders.models import orderdetails


def admin_dashboard(request):

    if "admin" not in request.session:
        return redirect("login")

    total_products = productdetails.objects.count()

    total_users = userdetails.objects.count()

    total_orders = orderdetails.objects.count()

    total_sales = sum(
        order.total_amount
        for order in orderdetails.objects.exclude(
            order_status="Cancelled"
        )
    )

    out_of_stock = productdetails.objects.filter(
        stock=0
    ).count()

    recent_orders = orderdetails.objects.all().order_by(
        "-order_date"
    )[:5]

    return render(request, "admin_dashboard.html", {
        "total_products": total_products,
        "total_users": total_users,
        "total_orders": total_orders,
        "total_sales": total_sales,
        "out_of_stock": out_of_stock,
        "recent_orders": recent_orders,
    })