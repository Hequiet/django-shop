from decimal import Decimal
from random import random, randrange

from django.core.management import BaseCommand
from shopapp.models import Product

class Command(BaseCommand):
    """
    Creates products
    """
    def handle(self, *args, **options):
        self.stdout.write('Creating products...')

        products_names = [
            ("Laptop", Decimal(100)),
            ("Desktop", Decimal(200)),
            ("Smartphone", Decimal(300)),
        ]
        for product_name in products_names:
            product, created = Product.objects.get_or_create(
                name=product_name[0], price=product_name[1])
            self.stdout.write(f'Created product: {product.name}')

        self.stdout.write(self.style.SUCCESS('Successfully created products'))