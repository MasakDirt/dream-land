from django.urls import path

from users.views import (
    UserDetailView,
    UserCreateView,
)

urlpatterns = [
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path(
        "create/",
        UserCreateView.as_view(),
        name="user-create"
    ),
]

app_name = "users"
