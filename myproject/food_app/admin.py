from django.contrib import admin
from .models import Dish, Orders, OrdersDish


class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'net_price', 'image')


admin.site.register(Dish, DishAdmin)
admin.site.register(Orders)
admin.site.register(OrdersDish)

