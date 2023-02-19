from django.forms import formset_factory
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from .models import Dish, Orders, OrdersDish
from .forms import OrderForm, OrderDishForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class HomeView(View):
    template_name = 'home.html'

    def get(self, request):
        dishes = Dish.objects.all()
        ctx = {
            'add_to_menu_url': 'add_to_menu',
            'place_order_url': 'place_order',
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


class OrderView(View):
    template_name = 'food_app/order.html'

    @method_decorator(login_required)
    def get(self, request):
        OrderDishFormSet = formset_factory(OrderDishForm)
        form = OrderForm()
        formset = OrderDishFormSet()
        dishes = Dish.objects.all()
        return render(request, 'food_app/order.html', {'form': form, 'formset': formset, 'dishes': dishes})

    @method_decorator(login_required)
    def post(self, request):
        OrderDishFormSet = formset_factory(OrderDishForm)
        form = OrderForm(request.POST)
        formset = OrderDishFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            for form in formset:
                dish = form.cleaned_data.get('dish')
                count = form.cleaned_data.get('count')
                OrdersDish.objects.create(dish=dish, orders=order, count=count, user=request.user)

            return redirect('home')

        return render(request, 'food_app/order.html', {'form': form, 'formset': formset})
