from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View


class ModelAddRemoveLike(LoginRequiredMixin, View):
    model = None
    model_like = None
    model_dislike = None

    def post(self, request: HttpRequest, **kwargs) -> HttpResponse:
        user = request.user
        instance = get_object_or_404(self.model, pk=kwargs.get("pk"))
        dict_model_name_and_instance = {self.model.__name__.lower(): instance}

        reaction_like = self.model_like.objects.filter(
            owner=user,
            **dict_model_name_and_instance
        )
        reaction_dislike = self.model_dislike.objects.filter(
            owner=user,
            **dict_model_name_and_instance
        )

        if reaction_dislike.exists():
            reaction_dislike.delete()

        if reaction_like.exists():
            reaction_like.delete()
        else:
            self.model_like.objects.create(
                owner=user,
                **dict_model_name_and_instance
            )

        next_url = request.POST.get("next", "dream:dream-list")
        return redirect(next_url)
