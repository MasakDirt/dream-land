from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from dream.views import ai_chat_views as chat_views
from dream.views.commentary import (
    CommentAddRemoveLike,
    CommentAddRemoveDislike,
    CommentaryCreateView,
    CommentaryDeleteView,
)
from dream.views.dream import (
    DreamListView,
    DreamDetailView,
    DreamCreateView,
    DreamUpdateView,
    DreamDeleteView,
    DreamAddRemoveLike,
    DreamAddRemoveDislike,
    DreamStatisticView,
    generate_dream_summary,
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
        "users/<int:pk>/dream-statistic/",
        DreamStatisticView.as_view(),
        name="user-dream-statistic"
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
    path(
        "users/<int:user_pk>/dreams/<int:dream_pk>/commentaries/create/",
        CommentaryCreateView.as_view(),
        name="commentary-create"
    ),
    path(
        "users/<int:user_pk>/dreams/<int:dream_pk>"
        "/commentaries/<int:pk>/delete/",
        CommentaryDeleteView.as_view(),
        name="commentary-delete"
    ),
    path(
        "users/<int:user_pk>/dreams/"
        "<int:dream_pk>/commentaries/<int:pk>/like/",
        CommentAddRemoveLike.as_view(),
        name="comment-like"
    ),
    path(
        "users/<int:user_pk>/dreams/<int:dream_pk>"
        "/commentaries/<int:pk>/dislike/",
        CommentAddRemoveDislike.as_view(),
        name="comment-dislike"
    ),

    path(
        "stats/generate-summary/<int:user_pk>/",
        generate_dream_summary,
        name="generate_dream_summary"
    ),

    # Chat
    # Chat pages
    path("chat/", chat_views.chat_page, name="chat"),
    path("chat/<int:thread_id>/", chat_views.chat_page, name="chat_thread"),

    # Chat API endpoints
    path("chat/new/", chat_views.new_thread, name="chat_new_thread"),
    path("chat/<int:thread_id>/send/", chat_views.send_message, name="chat_send"),
    path("chat/<int:thread_id>/load/", chat_views.load_thread, name="chat_load"),
    path("chat/<int:thread_id>/delete/", chat_views.delete_thread, name="chat_delete"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

app_name = "dream"
