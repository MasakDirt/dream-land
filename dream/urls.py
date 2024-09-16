from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from dream.views.dream import (
    DreamListView,
    DreamDetailView,
    DreamCreateView,
    DreamUpdateView,
    DreamDeleteView,
    DreamAddRemoveLike,
    DreamAddRemoveDislike
)
from dream.views.emotion import EmotionCreateView
from dream.views.index import index
from dream.views.symbol import SymbolCreateView


urlpatterns = [
    path("", index, name="index"),
    path(
        "symbols/create/",
        SymbolCreateView.as_view(),
        name="symbol-create"
    ),
    path(
        "emotions/create/",
        EmotionCreateView.as_view(),
        name="emotion-create"
    ),
    path("dreams/", DreamListView.as_view(), name="dream-list"),
    path(
        "users/<int:user_pk>/dreams/<int:pk>/",
        DreamDetailView.as_view(),
        name="dream-detail"
    ),
    path(
        "users/<int:user_pk>/dreams/create/",
        DreamCreateView.as_view(),
        name="dream-create"
    ),
    path(
        "users/<int:user_pk>/dreams/<int:pk>/update/",
        DreamUpdateView.as_view(),
        name="dream-update"
    ),
    path(
        "users/<int:user_pk>/dreams/<int:pk>/delete/",
        DreamDeleteView.as_view(),
        name="dream-delete"
    ),
    path(
        "users/<int:user_pk>/dreams/<int:pk>/like/",
        DreamAddRemoveLike.as_view(),
        name="dream-like"
    ),
    path(
        "users/<int:user_pk>/dreams/<int:pk>/dislike/",
        DreamAddRemoveDislike.as_view(),
        name="dream-dislike"
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

app_name = "dream"
