"""
В этом модуле лежат различные наборы представлений.

Разные View интернет-магазина: по товарам, заказам и тд
"""
from csv import DictWriter

from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.request import Request
from django.utils.decorators import method_decorator

from shopapp.common import save_csv_products
from shopapp.models import Product, Order
from shopapp.serializers import ProductSerializer, OrderSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse


@extend_schema(description='Product view CRUD')
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product
    Полный CRUD для сущностей товара
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (SearchFilter,
                       DjangoFilterBackend,
                       OrderingFilter,)
    search_fields = ('name', 'description')
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]
    ordering_fields = ['name',
                       'description',
                       'price',
                       'discount',
                       ]

    @extend_schema(
        summary='Get one product by ID',
        description='Retrieves **product**, returns 404 if not found',
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description='Empty response, product by ID not found')}
    )


    @method_decorator(cache_page(60 * 3))
    def list(self, *args, **kwargs):
        # print("hello product list")
        return super().list(*args, **kwargs)


    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @action(methods=['GET'], detail=False)
    def download_csv(self, request: Request) -> Response:
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })
        return response

    @action(methods=['POST'], detail=False, parser_classes=[MultiPartParser])
    def upload_csv(self, request: Request) -> Response:
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = (SearchFilter,
                       DjangoFilterBackend,
                       OrderingFilter,
                       )
    search_fields = ("delivery_address", "promocode")
    filterset_fields = [
        "delivery_address",
        "promocode",
        "created_at",
        "user_id",
    ]
    ordering_fields = ['user_id', 'created_at', ]
