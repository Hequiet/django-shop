from django.contrib.gis.feeds import Feed
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.urls import reverse, reverse_lazy
from blogapp.models import Article, ArticleOld


class BasedView(ListView):
    model = ArticleOld
    template_name = 'blogapp/article_old_list.html'
    context_object_name = 'articles_old'

    def get_queryset(self):
        return ((ArticleOld.objects.select_related('author', 'category')
                 .prefetch_related('tags'))
                .defer('content'))


class ArticleListView(ListView):
    queryset = (
        Article.objects
        .filter(published_at__isnull=False)
        .order_by('-published_at')
    )


class ArticleDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = 'Blog articles (latest)'
    description = 'Updates on changes and addition blog articles'
    link = reverse_lazy('blogapp:articles')

    def items(self):
        return (
            Article.objects
            .filter(published_at__isnull=False)
            .order_by('-published_at')[:5]
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.body[:200]

