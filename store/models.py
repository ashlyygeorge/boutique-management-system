from django.db import models
from accounts.models import userdetails


class productdetails(models.Model):

    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    ]

    product_name = models.CharField(max_length=100)

    product_category = models.CharField(max_length=100)

    product_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    product_description = models.TextField()

    product_image = models.ImageField(
        upload_to='products/'
    )

    stock = models.PositiveIntegerField()

    status = models.BooleanField(
        default=True
    )

    available_sizes = models.JSONField(
        default=list,
        blank=True
    )

    def __str__(self):
        return self.product_name


class Wishlist(models.Model):

    user = models.ForeignKey(
        userdetails,
        on_delete=models.CASCADE,
        related_name="wishlist"
    )

    product = models.ForeignKey(
        productdetails,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"