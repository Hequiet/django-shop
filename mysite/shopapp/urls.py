from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.decorators.cache import cache_page
from .views import (ShopIndexView,
                    ProductListView,
                    CreateProductView,
                    ProductDetailView,
                    OrderListView,
                    OrderCreateView,
                    OrderDetailView,
                    ProductUpdateView,
                    ProductDeleteView,
                    OrderUpdateView,
                    OrderDeleteView,
                    ProductsDataExportView,
                    OrdersDataExportView,
                    LatestProductsFeed,
                    UserOrdersListView,
                    UserOrderExportView,
                    )

from .api import ProductViewSet, OrderViewSet

app_name = "shopapp"

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)

urlpatterns = [
    # path("", cache_page(60 * 3)(ShopIndexView.as_view()), name="index"),
    path("", ShopIndexView.as_view(), name="index"),
    path("api/", include(routers.urls)),
    path('products/', ProductListView.as_view(), name="product_list"),
    path('products/<int:pk>/', ProductDetailView.as_view(), name="product_details"),
    path('products/create/', CreateProductView.as_view(), name="product_create"),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name="product_update"),
    path('products/<int:pk>/archived/', ProductDeleteView.as_view(), name="product_delete"),
    path('products/export/', ProductsDataExportView.as_view(), name="products_export"),
    path('orders/', OrderListView.as_view(), name="orders_list"),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name="order_details"),
    path('orders/<int:pk>/update', OrderUpdateView.as_view(), name="order_update"),
    path('orders/<int:pk>/delete', OrderDeleteView.as_view(), name="order_delete"),
    path('orders/create/', OrderCreateView.as_view(), name="order_create"),
    path('order/export/', OrdersDataExportView.as_view(), name="orders_export"),
    path('products/latest/feed/', LatestProductsFeed(), name="latest_products_feed"),
    path('users/<int:user_id>/orders/', UserOrdersListView.as_view(), name="users_orders"),
    path('users/<int:user_id>/orders/export', UserOrderExportView.as_view(), name="users_orders_export"),

]
