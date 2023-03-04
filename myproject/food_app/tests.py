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
        self.password = 'testpassword'
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password=self.password
        )
        self.dish_1 = Dish.objects.create(
            name='Pizza',
            net_price=25,
            description='Delicious pizza',
        )
        self.dish_2 = Dish.objects.create(
            name='Burger',
            net_price=15,
            description='Juicy burger',
        )

    def test_order_form_submission(self):
        self.client.login(username=self.user.username, password=self.password)

        order_data = {
            'customer_name': 'Test User',
            'customer_email': 'testuser@test.com',
            'customer_phone': '123456789',
            'customer_address': 'Test Address',
            'dishes': [self.dish_1.pk, self.dish_2.pk],
            'counts_{}'.format(self.dish_1.pk): [2],
            'counts_{}'.format(self.dish_2.pk): [3],
        }

        response = self.client.post('/order/', data=order_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your order has been successfully submitted')
        self.assertEqual(Orders.objects.count(), 1)
        self.assertEqual(OrdersDish.objects.count(), 2)


class OrderSuccessViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.dish_1 = Dish.objects.create(
            name='Pizza',
            net_price=25,
            description='Delicious pizza',
        )
        self.dish_2 = Dish.objects.create(
            name='Burger',
            net_price=15,
            description='Juicy burger',
        )
        self.order = Orders.objects.create(
            customer_name='Test User',
            customer_email='testuser@test.com',
            customer_phone='123456789',
            customer_address='Test Address',
            total_price=85,
        )
        self.order_dish_1 = self.order.ordersdish_set.create(
            dish=self.dish_1,
            count=2,
            user=None,
            price=50,
        )
        self.order_dish_2 = self.order.ordersdish_set.create(
            dish=self.dish_2,
            count=3,
            user=None,
            price=35,
        )

    def test_order_success_view(self):
        url = reverse('order-success', args=[self.order.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'food_app/order_success.html')
        self.assertContains(response, 'Test User')
        self.assertContains(response, 'testuser@test.com')
        self.assertContains(response, '123456789')
        self.assertContains(response, 'Test Address')
        self.assertContains(response, 'Pizza')
        self.assertContains(response, '2')
        self.assertContains(response, 'Burger')
        self.assertContains(response, '3')
        self.assertContains(response, '85')


class OrderHistoryViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.orders = Orders.objects.create(customer_name='Test Customer', customer_email='test@example.com',
                                            customer_phone='1234567890', customer_address='Test Address',
                                            total_price='10')
        self.url = reverse('order-history')

    def test_order_history_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'food_app/order_history.html')
        self.assertContains(response, 'Test Customer')
        self.assertContains(response, 'test@example.com')
        self.assertContains(response, '1234567890')
        self.assertContains(response, 'Test Address')
        self.assertContains(response, '10')
        self.assertQuerysetEqual(response.context['orders'], [repr(self.orders)])



