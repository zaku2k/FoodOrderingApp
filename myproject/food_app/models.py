from django.db import models
from django.contrib.auth.models import User


class Dish(models.Model):
    name = models.CharField(max_length=24)
    description = models.TextField()
    net_price = models.DecimalField(max_digits=4, decimal_places=2)
    image = models.ImageField()

    def __str__(self):
        return self.name


class Orders(models.Model):
    customer_name = models.CharField(max_length=24)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=9)
    created_at = models.DateTimeField(auto_now_add=True)
    customer_address = models.CharField(max_length=32, blank=False)


class OrdersDish(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    orders = models.ForeignKey(Orders, on_delete=models.CASCADE)
    count = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)


