from django.contrib.sitemaps import Sitemap
# custom imports
from .models import Post


def PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Post.published.all()
    
    def lastmod(self, obj):
        return obj.updated