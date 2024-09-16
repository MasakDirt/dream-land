from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import CreateView, DeleteView

from dream.forms import CommentaryForm
from dream.models import Commentary, CommentaryLike, CommentaryDislike, Dream


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


class CommentaryCreateView(LoginRequiredMixin, CreateView):
    model = Commentary
    form_class = CommentaryForm

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.owner = self.request.user
        dream = get_object_or_404(Dream, pk=self.kwargs.get("dream_pk"))
        comment.dream = dream
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")


class CommentaryDeleteView(LoginRequiredMixin, DeleteView):
    model = Commentary

    def delete(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        if not self.has_permission_to_delete():
            return HttpResponseForbidden(
                "You do not have permission to delete this commentary."
            )
        return super().delete(request, *args, **kwargs)

    def get_success_url(self) -> HttpResponse:
        return self.object.dream.get_absolute_url()

    def has_permission_to_delete(self) -> bool:
        return self.request.user == self.object.owner
