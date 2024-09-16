from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from dream.views.index import index
from dream.views.symbol import SymbolCreateView

urlpatterns = [
    path("", index, name="index"),
    path(
        "symbols/create/",
        SymbolCreateView.as_view(),
        name="symbol-create"
    )
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

app_name = "dream"
