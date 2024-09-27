from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DeleteView

from dream.forms import CommentaryForm
from dream.models import Commentary, CommentaryLike, CommentaryDislike, Dream
from dream.views.abstract import ModelAddRemoveLike


class CommentAddRemoveLike(ModelAddRemoveLike):
    model = Commentary
    model_like = CommentaryLike
    model_dislike = CommentaryDislike


class CommentAddRemoveDislike(ModelAddRemoveLike):
    model = Commentary
    model_like = CommentaryDislike
    model_dislike = CommentaryLike


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
        return self.object.dream.get_absolute_url()


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
