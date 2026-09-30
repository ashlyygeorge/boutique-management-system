"""
URL configuration for boutiquemanagementsystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path("checkout", views.checkout, name="checkout"),
    path("order_success", views.order_success, name="order_success"),
    path("order_history", views.order_history, name="order_history"),
    path("order_details/<int:id>/",views.order_details,name="order_details"),
    path("admin_orders", views.admin_orders, name="admin_orders"),
    path("update_order_status/<int:id>/",views.update_order_status,name="update_order_status"),
    path("cancel_order/<int:id>/", views.cancel_order, name="cancel_order"),
    path("payment_success", views.payment_success, name="payment_success"),

    

]
