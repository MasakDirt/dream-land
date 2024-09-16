from django.urls import path

from users.views import (
    UserDetailView,
    UserCreateView,
    UserDeleteView,
)

urlpatterns = [
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path(
        "create/",
        UserCreateView.as_view(),
        name="user-create"
    ),
    path(
        "<int:pk>/delete/",
        UserDeleteView.as_view(),
        name="user-delete"
    ),
]

app_name = "users"
