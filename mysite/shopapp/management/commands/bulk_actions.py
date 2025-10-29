
from django.core.management import BaseCommand
from django.contrib.auth.models import User

from shopapp.models import Product


class Command(BaseCommand):
    """
    Creates products
    """

    def handle(self, *args, **options):
        self.stdout.write('Start demo bulk actions')
        result = Product.objects.filter(
            name__contains='smartphone'
        ).update(discount=10)
        print(result)

        # info = [
        #     ('smartphone1', 199),
        #     ('smartphone2', 299),
        #     ('smartphone3', 399),
        # ]
        # products = [
        #     Product(name=name, price=price,created_by_id=1)
        #     for name, price in info
        # ]
        # result = Product.objects.bulk_create(products)
        #
        # for obj in result:
        #     print(obj)

        self.stdout.write("Done")
