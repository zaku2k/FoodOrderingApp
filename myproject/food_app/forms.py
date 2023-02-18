from django import forms
from django.forms import inlineformset_factory
from .models import Orders, OrdersDish, Dish


class OrderForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = ['customer_name', 'customer_email', 'customer_phone', 'customer_address']


class OrderDishForm(forms.ModelForm):
    dish = forms.ModelChoiceField(queryset=Dish.objects.all(), label='Dish')

    class Meta:
        model = OrdersDish
        fields = ['dish', 'count']

    def __init__(self, *args, **kwargs):
        super(OrderDishForm, self).__init__(*args, **kwargs)
        self.fields['dish'].queryset = Dish.objects.all().values('name', 'description', 'net_price')