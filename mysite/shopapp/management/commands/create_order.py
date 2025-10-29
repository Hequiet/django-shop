from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction
from typing import Sequence

from shopapp.models import Order, Product


class Command(BaseCommand):
    """
    Creates products
    """
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Creating order_with_products')
        user = User.objects.get(username='admin')
        products: Sequence[Product] = Product.objects.only("id").all()
        order, created = Order.objects.get_or_create(
            delivery_address="Ivanova",
            promocode="promo 4",
            user=user,
        )
        for product in products:
            order.products.add(product)
        order.save()
        self.stdout.write(self.style.SUCCESS(f'Created order {order}'))

        self.stdout.write(self.style.SUCCESS('Successfully created products'))
