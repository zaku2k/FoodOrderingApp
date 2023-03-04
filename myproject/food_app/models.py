from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User


class Dish(models.Model):
    name = models.CharField(max_length=24)
    description = models.TextField()
    net_price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'food_app_dish'


class Orders(models.Model):
    customer_name = models.CharField(max_length=24)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    customer_address = models.CharField(max_length=32, blank=False)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))

    def save(self, *args, **kwargs):
        if not self.pk:
            orders_dishes = OrdersDish.objects.filter(orders=self)
            total_price = sum([od.price for od in orders_dishes])
            self.total_price = total_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.customer_name} ({self.created_at})'

    class Meta:
        db_table = 'food_app_orders'


class OrdersDish(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    orders = models.ForeignKey(Orders, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.dish.name} ({self.orders.customer_name})'

    class Meta:
        db_table = 'food_app_orders_dish'

