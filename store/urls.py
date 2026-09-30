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
from. import views

urlpatterns = [
    path('add_product', views.add_product, name='add_product'),
    path('product_list', views.product_list, name='product_list'),
    path("product/<int:id>", views.product_details, name="product_details"),
    path("update_product/<int:id>", views.update_product, name="update_product"),
    path("delete_product/<int:id>", views.delete_product, name="delete_product"),
    path("remove_stock/<int:id>", views.remove_stock, name="remove_stock"),

    # Wishlist
    path("wishlist",views.wishlist,name="wishlist"),

    path("wishlist/add/<int:product_id>",views.add_to_wishlist,name="add_to_wishlist"),
    path("wishlist/remove/<int:product_id>",views.remove_from_wishlist,name="remove_from_wishlist" ),
    ]
        
        
        
   