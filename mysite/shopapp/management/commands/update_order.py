from django.core.management import BaseCommand

from shopapp.models import Order, Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        order = Order.objects.first()
        if not order:
            self.stdout.write(self.style.ERROR('No orders found'))
            return

        products = Product.objects.all()
        for product in products:
            order.products.add(product)

        self.stdout.write(
            self.style.SUCCESS
            (f'Successfully add order {order.products.all} to {order}'))