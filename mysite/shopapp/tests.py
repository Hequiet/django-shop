from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse
from string import ascii_letters
from random import choices

from shopapp.models import Product, Order
from shopapp.utils import add_two_numbers


class AddTwoNumbers(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class ProductCreateViewTestCase(TestCase):
    def setUp(self):
        self.product_name = ''.join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()
        self.user = User.objects.create_user(username='testuser', password='1234')
        permission = Permission.objects.get(
            codename='add_product'
        )

        self.user.user_permissions.add(permission)
        self.client.login(username='testuser', password='1234')


    def test_create_product(self):
        response = self.client.post(
            reverse("shopapp:product_create"),
            {'name': self.product_name,
             'description': "Good table",
             'price': "123.45",
             'discount': "18"
             }
        )
        self.assertRedirects(response, reverse("shopapp:product_list"))
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='testuser', password='1234')
        cls.product = Product.objects.create(name="Best product", created_by=cls.user)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        cls.product.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = ['auth-fixtures.json',
                'products-fixture.json',
                ]

    def test_products(self):
        response = self.client.get(reverse("shopapp:product_list"))
        self.assertQuerySetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context['products']),
            transform=lambda p: p.pk
        )
        self.assertTemplateUsed(response, "shopapp/products_list.html", )


class OrderListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='testuser', password='1234')
        cls.user = User.objects.create_user(**cls.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.login(**self.credentials)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, "Заказы")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = ['auth-fixtures.json',
                'products-fixture.json', ]

    def test_get_products_view(self):
        response = self.client.get(reverse("shopapp:products_export"))
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by('pk').all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,

            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(products_data["products"], expected_data)


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='testuser', password='1234')
        cls.user = User.objects.create_user(**cls.credentials)
        permission = Permission.objects.get(
            codename='view_order')
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.order = Order.objects.create(user_id=self.user.pk, delivery_address='Pushkina', promocode="2077")

    def tearDown(self):
        self.order.delete()

    def test_order_details(self):
        self.assertTrue(self.user.has_perm('shopapp.view_order'))
        response = self.client.get(reverse("shopapp:order_details", kwargs={"pk": self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pushkina')
        self.assertContains(response, '2077')

        order = response.context['order']
        self.assertEqual(order.pk, self.order.pk)
        self.assertEqual(order.delivery_address, self.order.delivery_address)
        self.assertEqual(order.promocode, self.order.promocode)


class OrdersExportTestCase(TestCase):
    fixtures = ["auth-fixtures.json",
                "order-fixture.json",
                "products-fixture.json",
                ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.credentials = dict(username='testuser', password='1234', is_staff=True)
        cls.user = User.objects.create_user(**cls.credentials)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_orders_export(self):
        response = self.client.get(reverse("shopapp:orders_export"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        orders = Order.objects.all()

        expected_data = [
            {"pk": order.pk,
             "delivery_address": order.delivery_address,
             "promocode": order.promocode,
             "products": [product.id for product in order.products.all()],
             "user_id": order.user_id,
             }
            for order in orders
        ]

        data = response.json()
        self.assertIn("orders", data)
        orders_data = data["orders"]
        self.assertIsInstance(orders_data, list)
        self.assertIn('orders', data)
        self.assertGreater(len(orders_data), 0)

        self.assertEqual(orders_data, expected_data)


    def test_orders_export_json_anonymous_user(self):
        self.client.logout()
        url = reverse("shopapp:orders_export")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_orders_export_json_regular_user(self):

        regular_user = User.objects.create_user(
            username='regular',
            password='123',
            is_staff=False
        )
        self.client.login(username='regular', password='123')
        url = reverse("shopapp:orders_export")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)