from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
    HttpRequest
)
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    DetailView,
    CreateView,
    DeleteView, UpdateView, View,
)

from dto.dto import DreamListDto
from users.forms import CustomUserCreateForm
from users.models import Profile, Follow


class UserDetailView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    context_object_name = "current_user"

    def get_object(self, queryset=None) -> settings.AUTH_USER_MODEL:
        return get_user_model().objects.select_related(
            "profile"
        ).prefetch_related(
            "dream_likes",
            "dream_dislikes",
            "commentaries",
            "dreams",
            "dreams__user",
            "dreams__user__profile",
            "dreams__likes",
            "dreams__dislikes",
            "dreams__commentaries",
            "dreams__commentaries__owner__profile",
            "dreams__commentaries__likes",
            "dreams__commentaries__dislikes",
            "followers__follower",
            "followers__followed",
            "followers__followed__profile",
            "followers__follower__profile",
        ).get(pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs) -> dict:
        context = super(UserDetailView, self).get_context_data(**kwargs)

        current_user = context.get("current_user")
        current_user.dream_dtos = [
            DreamListDto.get_from_dream(
                dream,
                self.request.COOKIES.get(str(dream.pk), False)
            )
            for dream in current_user.dreams.all()
        ]

        top_emotion = current_user.dreams.values("emotions__name").annotate(
            count=Count("emotions__name")
        ).order_by(
            "-count",
            "emotions__name"
        ).values_list(
            "emotions__name",
            "count"
        ).first()

        top_symbol = current_user.dreams.values("symbols__name").annotate(
            count=Count("symbols__name")
        ).order_by(
            "-count",
            "symbols__name"
        ).values_list(
            "symbols__name",
            "count"
        ).first()

        context["current_user"] = current_user
        context["top_emotion"] = top_emotion[0] if top_emotion else ""
        context["top_symbol"] = top_symbol[0] if top_symbol else ""

        return context


class UserCreateView(CreateView):
    model = get_user_model()
    form_class = CustomUserCreateForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = get_user_model()

    def delete(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        if not self.has_permission_to_delete():
            return HttpResponseForbidden(
                "You do not have permission to delete this user."
            )
        return super().delete(request, *args, **kwargs)

    def get_success_url(self) -> HttpResponse:
        return reverse("dream:index")

    def has_permission_to_delete(self) -> bool:
        return self.request.user == self.object


class ProfileCreateView(LoginRequiredMixin, CreateView):
    model = Profile
    fields = ("bio", "profile_picture")
    template_name = "users/profile_form.html"

    def form_valid(self, form) -> HttpResponseRedirect:
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> HttpResponse:
        return reverse_lazy(
            "users:user-detail",
            kwargs={"pk": self.request.user.pk}
        )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ("bio", "profile_picture")
    template_name = "users/profile_form.html"

    def form_valid(self, form) -> HttpResponseRedirect:
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> HttpResponse:
        return reverse_lazy(
            "users:user-detail",
            kwargs={"pk": self.request.user.pk}
        )


class FollowView(LoginRequiredMixin, View):
    def post(
            self, request: HttpRequest,
            followed_pk: str,
            follower_pk: str
    ) -> HttpResponse:
        user_followed = get_object_or_404(get_user_model(), pk=followed_pk)
        user_follower = get_object_or_404(get_user_model(), pk=follower_pk)

        if Follow.is_following(user_follower, user_followed):
            Follow.objects.filter(
                follower=user_follower,
                followed=user_followed
            ).delete()
        else:
            Follow.objects.create(
                follower=user_follower,
                followed=user_followed
            )

        return redirect("users:user-detail", pk=followed_pk)


class FollowersListView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, pk: str) -> HttpResponse:
        user = get_object_or_404(get_user_model(), pk=pk)
        queryset = user.followers.select_related(
            "follower"
        ).prefetch_related(
            "follower__dreams",
            "follower__followers",
            "follower__following"
        )

        context = {
            "followers": queryset,
            "current_user": user,
        }

        return render(
            request,
            "users/followers_list.html",
            context=context
        )


class FollowedListView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, pk: str) -> HttpResponse:
        user = get_object_or_404(get_user_model(), pk=pk)
        queryset = user.following.select_related(
            "followed"
        ).prefetch_related(
            "followed__dreams",
            "followed__followers",
            "followed__following"
        )

        context = {
            "following": queryset,
            "current_user": user,
        }

        return render(
            request,
            "users/following_list.html",
            context=context
        )
