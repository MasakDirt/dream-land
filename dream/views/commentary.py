from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from dream.models import Commentary, CommentaryLike, CommentaryDislike


class CommentAddRemoveLike(LoginRequiredMixin, View):
    def post(
            self, request: HttpRequest,
            user_pk: str,
            dream_pk: str,
            pk: str,
    ) -> HttpResponse:
        user = request.user
        commentary = get_object_or_404(Commentary, pk=pk)
        commentary_like = CommentaryLike.objects.filter(
            owner=user,
            commentary=commentary
        )
        commentary_dislike = CommentaryDislike.objects.filter(
            owner=user,
            commentary=commentary
        )

        if commentary_dislike.exists():
            commentary_dislike.delete()

        if commentary_like.exists():
            commentary_like.delete()
        else:
            CommentaryLike.objects.create(owner=user, commentary=commentary)

        return redirect(
            self.request.META.get(
                "HTTP_REFERER",
                "dream:dream-list",
            )
        )

class CommentAddRemoveDislike(LoginRequiredMixin, View):
    def post(
            self, request: HttpRequest,
            user_pk: str,
            dream_pk: str,
            pk: str,
    ) -> HttpResponse:
        user = request.user
        commentary = get_object_or_404(Commentary, pk=pk)
        commentary_like = CommentaryLike.objects.filter(
            owner=user,
            commentary=commentary
        )
        commentary_dislike = CommentaryDislike.objects.filter(
            owner=user,
            commentary=commentary
        )

        if commentary_like.exists():
            commentary_like.delete()

        if commentary_dislike.exists():
            commentary_dislike.delete()
        else:
            CommentaryDislike.objects.create(owner=user, commentary=commentary)

        return redirect("dream:dream-detail", user_pk=user_pk, pk=dream_pk)
