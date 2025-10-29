from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return "products/product_{pk}/preview/{filename}".format(
        pk=instance.pk, filename=filename
    )

class Product(models.Model):
    """
    Модель Product представляет товар,
    который можно продавать в интернет магазине

    Заказы тут: :model:`shopapp.Order`
    """
    name = models.CharField(max_length=100, verbose_name=_("Product name"), db_index=True)
    description = models.TextField(null=False, blank=True, verbose_name=_("Product description"),db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2, verbose_name=_("Product price"))
    discount = models.SmallIntegerField(default=0, verbose_name=_("Product discount"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Product created"))
    archived = models.BooleanField(default=False, verbose_name=_("Product archived"))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Product created by"))
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path, verbose_name=_("Product preview"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return f"Product(pk={self.pk}, name={self.name})"

    def get_absolute_url(self):
        return reverse('shopapp:product_details', kwargs={'pk': self.pk})


def product_image_directory_path(instance: "ProductImage", filename: str) -> str:
    return "products/product_{pk}/image/{filename}".format(
        pk=instance.product.pk, filename=filename
    )

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(null=True, blank=True, upload_to=product_image_directory_path)
    description = models.CharField(max_length=200, null=False, blank=True)

class Order(models.Model):
    delivery_address = models.TextField(null=True, blank=True, verbose_name=_("Delivery address"))
    promocode = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("Promocode"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Order created"))
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_("Order user"))
    products = models.ManyToManyField(Product, related_name='orders', verbose_name=_("Order products"))
    receipt = models.FileField(null=True, upload_to='order/receipts', verbose_name=_("Receipt"))

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f"Order(pk={self.pk})"
