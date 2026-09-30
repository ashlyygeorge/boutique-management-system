
from django.db import models


class userdetails(models.Model):
    username = models.CharField(max_length=100)
    useremail = models.EmailField(max_length=100, unique=True)
    userphone = models.CharField(max_length=10)
    userpassword = models.CharField(max_length=128)

    def __str__(self):
        return self.username

