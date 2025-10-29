from django.contrib.sitemaps import Sitemap
from .models import Product

class ShopSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.6
    def items(self):
        return Product.objects.filter(archived=False).order_by('name')

    def lastmod(self, obj: Product):
        return obj.created_at
