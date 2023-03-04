from sqlite3 import IntegrityError

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse
from .models import Dish, Orders, OrdersDish


class RegisterViewGetTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('register')

    def test_register_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'food_app/register.html')
        self.assertIsInstance(response.context['form'], UserCreationForm)


class RegisterViewPostValidFormTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('register')

    def test_register_view_post_valid_form(self):
        data = {'username': 'testuser', 'password1': 'testpass123', 'password2': 'testpass123'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='testuser').exists())


class RegisterViewPostInvalidFormTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('register')

    def test_register_view_post_invalid_form(self):
        data = {'username': '', 'password1': 'testpass123', 'password2': 'testpass123'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'food_app/register.html')
        self.assertIsInstance(response.context['form'], UserCreationForm)
        self.assertContains(response, '<ul class="errorlist">')


User = get_user_model()


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('login')

    def test_login_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'food_app/login.html')
        self.assertIsInstance(response.context['form'], AuthenticationForm)

    def test_login_view_post_valid_credentials(self):
        username = 'testuser'
        password = 'testpass123'
        user = User.objects.create_user(username=username, password=password)
        data = {'username': username, 'password': password}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(user.is_authenticated)

    def test_login_view_post_invalid_credentials(self):
        data = {'username': 'invaliduser', 'password': 'invalidpass123'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'food_app/login.html')
        self.assertIsInstance(response.context['form'], AuthenticationForm)
        self.assertContains(response, 'Wprowadź poprawne wartości pól nazwa użytkownika oraz hasło. Uwaga: wielkość liter ma znaczenie.')
        self.assertContains(response, '<form method="post">')
        self.assertContains(response, '<button type="submit">Zaloguj się</button>', html=True)


class LogoutViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

    def test_authenticated_user_is_logged_out(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('logout'))

        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_message_is_displayed_after_logging_out(self):

        self.client.force_login(self.user)
        response = self.client.get(reverse('logout'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Zostałeś wylogowany.')

        self.assertRedirects(response, reverse('login'))


class OrderViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuserr2', password='testpass')
        self.client.login(username='testuserr2', password='testpass')
        self.dish = Dish.objects.create(name='Test Dish', description='Test Description', net_price='10.99')
        self.order = Orders.objects.create(
            customer_name='Test Customer',
            customer_email='test@test.com',
            customer_phone='1234567890',
            customer_address='Test Address',
        )
        self.order.user = self.user
        self.order.save()
        OrdersDish.objects.create(
            dish=self.dish,
            orders=self.order,
            count=1,
            price=self.dish.net_price,
            user=self.user
        )
        self.order_data = {
            'customer_name': 'Test Customer',
            'customer_email': 'test@test.com',
            'customer_phone': '1234567890',
            'customer_address': 'Test Address',
            'dishes': [self.dish.id],
        }

    def test_order_creation(self):
        response = self.client.post('/order/', data=self.order_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'food_app/order_success.html')
        orders = Orders.objects.all()
        self.assertEqual(len(orders), 2) # jedno zamówienie z testu, drugie z setUpTestData
        orders_dish = OrdersDish.objects.all()
        self.assertEqual(len(orders_dish), 2)
        self.assertEqual(orders_dish[1].count, 1) # indeksowanie od 1, bo pierwsze zamówienie jest z setUpTestData
        self.assertEqual(orders_dish[1].dish, self.dish)
        self.assertEqual(orders_dish[1].orders, self.order)
        self.assertEqual(orders_dish[1].user, self.user)





