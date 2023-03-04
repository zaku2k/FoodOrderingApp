from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import View, ListView, TemplateView
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from .models import Dish, Orders, OrdersDish
from .forms import OrdersForm


class HomeView(View):
    template_name = 'home.html'

    def get(self, request):
        dishes = Dish.objects.all()
        ctx = {
            'add_to_menu_url': 'add_to_menu',
            'place_order_url': 'place_order',
            'order_history_url': 'order_history',
            'register_url': 'register',
            'login_url': 'login',
            'logout_url': 'logout',
            'dishes': dishes
        }
        if request.user.is_authenticated:
            ctx['username'] = request.user.username

        return render(request, 'food_app/home.html', ctx)


class RegisterView(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'food_app/register.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Konto zostało utworzone dla użytkownika {username}')
            return redirect('login')
        else:
            return render(request, 'food_app/register.html', {'form': form})


class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'food_app/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'Zalogowałeś się jako {username}')
                return redirect('home')
            else:
                messages.error(request, 'Nieprawidłowy login lub hasło')
        else:
            messages.error(request, 'Nieprawidłowy login lub hasło')
            return render(request, 'food_app/login.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "Zostałeś wylogowany.")
        return redirect('login')


@method_decorator(login_required, name='dispatch')
class OrderView(View):
    template_name = 'food_app/order.html'
    success_template_name = 'food_app/order_success.html'
    form_class = OrdersForm

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        dishes = Dish.objects.prefetch_related('ordersdish_set').annotate(num_orders=Count('ordersdish')).all()
        form = self.form_class(initial={'counts': [1] * len(dishes)})
        context = {
            'dishes': dishes,
            'form': form,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        if request.method == 'POST':
            customer_name = request.POST.get('customer_name')
            customer_email = request.POST.get('customer_email')
            customer_phone = request.POST.get('customer_phone')
            customer_address = request.POST.get('customer_address')

            orders = Orders.objects.create(
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                customer_address=customer_address
            )

            total_price = 0
            for i in range(len(request.POST.getlist('dishes'))):
                dish_id = int(request.POST.getlist('dishes')[i])
                count = int(request.POST.getlist('counts_{}'.format(i))[0])
                dish = Dish.objects.get(pk=dish_id)
                price = dish.net_price * count
                total_price += dish.net_price * count
                OrdersDish.objects.create(
                    orders=orders,
                    dish=dish,
                    count=count,
                    price=price,
                )

            orders.total_price = total_price
            orders.save()

            return render(request, self.success_template_name, {'order': orders})

        return HttpResponseNotAllowed(['POST'])


class OrderSuccessView(TemplateView):
    template_name = 'food_app/order_success.html'

    def get(self, request, *args, **kwargs):
        order_id = kwargs['order_id']
        order = Orders.objects.get(pk=order_id)
        context = {
            'order': order,
        }
        return render(request, self.template_name, context)


class OrderHistoryView(LoginRequiredMixin, ListView):
    template_name = 'food_app/order_history.html'
    model = Orders
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().filter(ordersdish__user=self.request.user).order_by('-created_at').distinct()




