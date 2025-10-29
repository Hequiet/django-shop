from csv import DictReader
from io import TextIOWrapper

from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect

from shopapp.models import Product, Order


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)
    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products


def save_csv_orders(request, file):
    csv_file = TextIOWrapper(
        file,
        encoding=request.encoding,
    )
    reader = DictReader(csv_file)
    for row in reader:
        try:
            user = row.get('user_id')
            User.objects.get(id=user)
            order = Order.objects.create(
                delivery_address=row.get('delivery_address', ""),
                promocode=row.get('promocode', ""),
                user_id=row.get('user_id', "")
            )
        except User.DoesNotExist:
            messages.error(request, f"User with id {user} does not exist")
            continue
        product_ids = row.get('products', "")
        if product_ids:
            try:
                ids = [int(id) for id in product_ids.split(',')]
                product = Product.objects.filter(id__in=ids)
                order.products.set(product)

            except (ValueError, TypeError):
                messages.warning(
                    request,
                    f"Incorrect product IDs in the row: {product_ids}"
                )
