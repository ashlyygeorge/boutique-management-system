from django.db import models

class cartdetails(models.Model):
    username = models.CharField(max_length=100)
    productname = models.CharField(max_length=100)
    productid = models.IntegerField(default=0)
    productprice = models.IntegerField()
    quantity = models.IntegerField()