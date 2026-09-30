from django.db import models


class orderdetails(models.Model):

    customer = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=50,
        default="Cash on Delivery"
    )

    razorpay_order_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    razorpay_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    order_date = models.DateTimeField(auto_now_add=True)

    order_status = models.CharField(
        max_length=50,
        default="Pending"
    )


class orderitems(models.Model):

    order = models.ForeignKey(
        orderdetails,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        "store.productdetails",
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def item_total(self):
        return self.price * self.quantity

    def __str__(self):
        return self.product.product_name