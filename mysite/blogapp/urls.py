from django.urls import path
from .views import (BasedView,
                    ArticleListView,
                    ArticleDetailView,
                    LatestArticlesFeed,
                    )



app_name = "blogapp"

urlpatterns = [
    path("articles_old/", BasedView.as_view(), name="articles"),
    path("articles/", ArticleListView.as_view(), name="articles"),
    path("articles/<int:pk>/", ArticleDetailView.as_view(), name="article"),
    path("articles/latest/feed/", LatestArticlesFeed(), name="latest"),
]