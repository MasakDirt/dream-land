from django.urls import path

from users.views import (
    UserDetailView,
    UserCreateView,
    UserDeleteView,
    ProfileCreateView,
    ProfileUpdateView, FollowView, FollowedListView, FollowersListView,
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
    path(
        "<int:user_pk>/profile/create/",
        ProfileCreateView.as_view(),
        name="profile-create"
    ),
    path(
        "<int:user_pk>/profile/<int:pk>/update/",
        ProfileUpdateView.as_view(),
        name="profile-update"
    ),
    path(
        "<int:followed_pk>/follow/<int:follower_pk>/",
        FollowView.as_view(),
        name="user-follow"
    ),
]

app_name = "users"
