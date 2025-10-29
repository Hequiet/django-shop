from rest_framework import serializers
from .models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "pk",
            "name",
            "description",
            "price",
            "discount",
            "created_at",
            "archived",
            "preview",
        ]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "pk",
            "delivery_address",
            "promocode",
            "created_at",
            "user_id",
            "receipt",
        ]


def serialize_user_orders(orders):
    return [
        {"pk": order.pk,
         "delivery_address": order.delivery_address,
         "promocode": order.promocode,
         "products": [product.id for product in order.products.all()],
         }
        for order in orders
    ]
