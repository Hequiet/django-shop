from django.core.management import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Sum, Avg, Max, Min, Count

from shopapp.models import Order, Product


class Command(BaseCommand):
    """
    Creates products
    """

    def handle(self, *args, **options):
        self.stdout.write('Start demo agg')
        orders = Order.objects.annotate(
            total=Sum('products__price', default=0),
            products_count=Count('products')
        )
        for order in orders:
            print(f"Order: {order.id} with {order.products_count} "
                  f"products worth {order.total}")
        # result = Product.objects.filter(
        #     name__contains="smartphone").aggregate(
        #     Avg('price'),
        #     Max('price'),
        #     min_price=Min('price'),
        #     count=Count('price'),
        # )
        # print(result)
        self.stdout.write("Done")
