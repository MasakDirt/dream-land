from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    DetailView,
    CreateView,
    DeleteView,
)

from dto.dto import DreamListDto
from users.forms import CustomUserCreateForm


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
