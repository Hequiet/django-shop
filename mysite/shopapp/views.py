import logging

from django.contrib.auth import get_user_model
from django.contrib.gis.feeds import Feed
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import FileFieldForm
from shopapp.models import Product, Order, ProductImage
from .serializers import serialize_user_orders

log = logging.getLogger(__name__)

User = get_user_model()


class ShopIndexView(View):
    # @method_decorator(cache_page(60 * 3))
    def get(self, request):
        links_list = [
            {'url': 'products/', 'name': 'Список продуктов'},
            {'url': 'orders/', 'name': 'Список заказов'}
        ]
        products = Product.objects.all()
        context = {
            'title': 'Главная страница',
            'links': links_list,
            'products': products,
            'items': 1,
        }
        print("shop index context", context)
        log.debug("Product for shop index: %s", products)
        log.info("Rendering shop index")
        return render(request, 'shopapp/shop-index.html', context=context)


class ProductListView(ListView):
    template_name = 'shopapp/products_list.html'
    queryset = Product.objects.filter(archived=False)
    context_object_name = 'products'


class CreateProductView(PermissionRequiredMixin, CreateView):
    permission_required = ('shopapp.add_product')
    model = Product
    fields = 'name', 'description', 'price', 'discount', 'preview'
    success_url = reverse_lazy('shopapp:product_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    template_name_suffix = '_update_form'
    form_class = FileFieldForm

    def get_success_url(self):
        return reverse('shopapp:product_details', kwargs={'pk': self.object.pk})

    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        if user.is_superuser:
            return True
        return obj.created_by == user and user.has_perm('shopapp.change_product')

    def form_valid(self, form):
        files = form.cleaned_data["file_field"]
        for f in files:
            ProductImage.objects.create(
                product=self.object,
                image=f,
            )
        return super().form_valid(form)


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:product_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class ProductDetailView(DetailView):
    template_name = 'shopapp/product-details.html'
    queryset = Product.objects.prefetch_related('images')
    context_object_name = 'product'


class ProductsDataExportView(View):
    def get(self, request) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,

                }
                for product in products
            ]
            cache.set(cache_key, products_data, timeout=300)
        return JsonResponse({"products": products_data})


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'shopapp/order_list.html'
    model = Order
    context_object_name = 'orders'


class OrderCreateView(CreateView):
    model = Order
    fields = "delivery_address", "promocode", "user", "products"
    success_url = reverse_lazy('shopapp:orders_list')


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'shopapp.view_order'
    template_name = 'shopapp/order-detail.html'
    model = Order
    context_object_name = 'order'


class OrderUpdateView(UpdateView):
    model = Order
    fields = 'delivery_address', 'promocode', 'user', 'products'
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse('shopapp:order_details', kwargs={'pk': self.object.pk})


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('shopapp:orders_list')


class OrdersDataExportView(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        orders_data = [
            {"pk": order.pk,
             "delivery_address": order.delivery_address,
             "promocode": order.promocode,
             "products": [product.id for product in order.products.all()],
             "user_id": order.user_id,
             }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})


class LatestProductsFeed(Feed):
    title = 'Products name(latest)'
    description = 'The appearance of new products'
    link = reverse_lazy('shopapp:product_list')

    def items(self):
        return (Product.objects.
                filter(archived=False).
                order_by("-pk"))

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description


class UserOrdersListView(LoginRequiredMixin, ListView):
    template_name = 'shopapp/user_orders.html'
    model = Order
    context_object_name = 'orders'

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        self.owner = get_object_or_404(User, id=user_id)
        return Order.objects.filter(user_id=self.owner).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["owner"] = self.owner
        context["user"] = self.request.user.id
        return context


class UserOrderExportView(LoginRequiredMixin, View):
    model = Order

    def get(self, request, *args, **kwargs) -> JsonResponse:
        user_id = self.kwargs["user_id"]
        cache_key = "user_orders_export_{}".format(user_id)
        orders_data = cache.get(cache_key)
        print(f"Test data {orders_data}")
        if orders_data is not None:
            return JsonResponse({"orders": orders_data})

        owner = get_object_or_404(User, id=user_id)
        orders = Order.objects.filter(user_id=owner).order_by("pk")
        serialized_orders = serialize_user_orders(orders)
        orders_data = {
            "user_id": user_id,
            "user name": owner.username,
            "orders": serialized_orders,
        }
        cache.set(cache_key, orders_data, timeout=300)
        return JsonResponse({"orders": orders_data})
