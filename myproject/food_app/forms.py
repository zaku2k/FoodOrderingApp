from django import forms
from .models import Orders, OrdersDish, Dish


class OrdersForm(forms.ModelForm):
    dishes = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=Dish.objects.all(),
        required=False
    )
    counts = forms.IntegerField(widget=forms.HiddenInput(), required=False, min_value=1)
    total_price = forms.DecimalField(required=False)

    class Meta:
        model = Orders
        fields = ['customer_name', 'customer_email', 'customer_phone', 'customer_address', 'dishes', 'total_price']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.initial['counts'] = [1] * len(self.fields['dishes'].queryset)

    def save(self, commit=True):
        order = super().save(commit=False)
        if commit:
            order.save()

            # Only update total_price if it's not a new order
            if self.instance:
                total_price = sum(dish.net_price * count for dish, count in
                                  zip(self.cleaned_data['dishes'], self.cleaned_data['counts']) if count > 0)
                print(f"Before save: total_price = {order.total_price}")
                order.total_price = total_price
                order.save(update_fields=['total_price'])
                print(f"After save: total_price = {order.total_price}")

        for i, dish in enumerate(self.cleaned_data['dishes']):
            count = self.cleaned_data['counts'][i]
            if count > 0:
                OrdersDish.objects.create(
                    dish=dish,
                    orders=order,
                    count=count,
                    user=self.user,
                    price=dish.net_price * count,
                )

        return order


