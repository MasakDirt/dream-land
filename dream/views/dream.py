from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import (
    Count,
    Case,
    When,
    Q,
    Value,
    IntegerField,
    QuerySet
)
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    View
)

from dream.forms import (
    DreamFilterForm,
    DreamSearchForm,
    CommentaryForm,
    DreamForm
)
from dream.models import Dream, Symbol, Emotion, DreamLike, DreamDislike
from dto.dto import DreamListDto, EmotionDto, SymbolDto


class DreamListView(LoginRequiredMixin, ListView):
    model = Dream
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        context = super(DreamListView, self).get_context_data(**kwargs)

        dream_dtos = [
            DreamListDto.get_from_dream(
                dream,
                self.request.COOKIES.get(str(dream.pk), False)
            )
            for dream in context["dream_list"]
        ]

        title = self.request.GET.get("title", "")
        filter_by = self.request.GET.get("filter", "-date_recorded")

        context["dreams"] = dream_dtos
        context["dream_search"] = DreamSearchForm(initial={"title": title})
        context["filter"] = DreamFilterForm(initial={"filter": filter_by})

        return context

    def get_queryset(self) -> QuerySet[Dream]:
        self.queryset = (
            Dream.objects.prefetch_related(
                "user__profile",
                "commentaries",
                "dislikes",
                "likes"
            )
        )
        search_form = DreamSearchForm(self.request.GET)
        if search_form.is_valid():
            title_cleaned_data = search_form.cleaned_data["title"]
            if title_cleaned_data:
                self.queryset = self.queryset.annotate(
                    order=Case(
                        When(
                            Q(title__icontains=title_cleaned_data) &
                            Q(description__icontains=title_cleaned_data),
                            then=Value(3)
                        ),
                        When(
                            title__icontains=title_cleaned_data,
                            then=Value(2)
                        ),
                        When(
                            description__icontains=title_cleaned_data,
                            then=Value(1)
                        ),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                ).filter(order__gt=0).order_by("-order", "-date_recorded")

        filter_form = DreamFilterForm(self.request.GET)
        if filter_form.is_valid():
            filter_cleaned_data = filter_form.cleaned_data["filter"]
            if filter_cleaned_data == "likes":
                self.queryset = self.queryset.annotate(
                    like_count=Count("likes__dream")
                ).order_by("-like_count", "-date_recorded")
            elif filter_cleaned_data == "dislikes":
                self.queryset = self.queryset.annotate(
                    dislike_count=Count("dislikes__dream")
                ).order_by("-dislike_count", "-date_recorded")
            else:
                self.queryset = self.queryset.order_by(
                    filter_cleaned_data
                )

        return self.queryset


class DreamDetailView(LoginRequiredMixin, DetailView):
    model = Dream

    def get_object(self, queryset: QuerySet = None) -> Dream:
        dream_pk = self.kwargs["pk"]
        dream = Dream.objects.select_related("user").prefetch_related(
            "user__profile",
            "likes",
            "dislikes",
            "emotions",
            "symbols",
            "commentaries__owner__profile",
            "commentaries__likes",
            "commentaries__dislikes",
        ).get(pk=dream_pk)

        return dream

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        response = super().get(self, request, *args, **kwargs)
        pk = str(kwargs["pk"])
        is_visited = request.COOKIES.get(pk, False)
        if not is_visited:
            response.set_cookie(pk, True)

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = CommentaryForm
        return context


class DreamCreateView(LoginRequiredMixin, CreateView):
    model = Dream
    form_class = DreamForm

    def get_context_data(self, **kwargs) -> dict:
        context = super(DreamCreateView, self).get_context_data(**kwargs)
        context["emotions"] = Emotion.objects.all()
        context["symbols"] = Symbol.objects.all()

        return context

    def form_valid(self, form) -> DreamForm:
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> HttpResponse:
        return reverse_lazy(
            "users:user-detail",
            kwargs={"pk": self.request.user.pk}
        )


class DreamUpdateView(LoginRequiredMixin, UpdateView):
    model = Dream
    form_class = DreamForm

    def get_context_data(self, **kwargs) -> dict:
        context = super(DreamUpdateView, self).get_context_data(**kwargs)
        dream = context["dream"]
        dream.symbol_names = [
            name[0]
            for name in dream.symbols.values_list("name").distinct()
        ]
        dream.emotion_names = [
            name[0]
            for name in dream.emotions.values_list("name").distinct()
        ]
        context["emotions"] = Emotion.objects.all()
        context["symbols"] = Symbol.objects.all()

        return context

    def form_valid(self, form) -> DreamForm:
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> HttpResponse:
        return reverse_lazy(
            "users:user-detail",
            kwargs={"pk": self.request.user.pk}
        )


class DreamDeleteView(LoginRequiredMixin, DeleteView):
    model = Dream

    def delete(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        if not self.has_permission_to_delete():
            return HttpResponseForbidden(
                "You do not have permission to delete this dream."
            )
        return super().delete(request, *args, **kwargs)

    def get_success_url(self) -> HttpResponse:
        return self.object.user.get_absolute_url()

    def has_permission_to_delete(self) -> bool:
        return self.request.user == self.object.user


class DreamAddRemoveLike(LoginRequiredMixin, View):
    def post(
            self, request: HttpRequest,
            user_pk: str,
            pk: str
    ) -> HttpResponse:
        user = request.user
        dream = get_object_or_404(Dream, pk=pk)
        dream_like = DreamLike.objects.filter(owner=user, dream=dream)
        dream_dislike = DreamDislike.objects.filter(owner=user, dream=dream)

        if dream_dislike.exists():
            dream_dislike.delete()

        if dream_like.exists():
            dream_like.delete()
        else:
            DreamLike.objects.create(owner=user, dream=dream)

        return redirect(self.request.META.get(
            "HTTP_REFERER",
            "dream:dream-list",
        ))


class DreamAddRemoveDislike(LoginRequiredMixin, View):
    def post(
            self, request: HttpRequest,
            user_pk: str,
            pk: str
    ) -> HttpResponse:
        user = request.user
        dream = get_object_or_404(Dream, pk=pk)
        dream_like = DreamLike.objects.filter(owner=user, dream=dream)
        dream_dislike = DreamDislike.objects.filter(owner=user, dream=dream)

        if dream_like.exists():
            dream_like.delete()

        if dream_dislike.exists():
            dream_dislike.delete()
        else:
            DreamDislike.objects.create(owner=user, dream=dream)

        return redirect(self.request.META.get(
            "HTTP_REFERER",
            "dream:dream-list",
        ))


class DreamStatisticView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, pk: str) -> HttpResponse:
        user = get_user_model().objects.prefetch_related(
            "dreams__emotions",
            "dreams__symbols",
        ).get(pk=pk)
        dreams = user.dreams.all()

        top_of_emotions = EmotionDto.get_from_query_set(
            dreams.values("emotions__name", "emotions__description").annotate(
                total_count=Count("emotions__name")
            ).order_by("-total_count", "emotions__name")[:8]
        )

        top_of_symbols = SymbolDto.get_from_query_set(
            dreams.values("symbols__name", "symbols__description").annotate(
                total_count=Count("symbols__name")
            ).order_by("-total_count", "symbols__name")[:8]
        )

        context = {
            "current_user": user,
            "count_dreams": user.dreams.count(),
            "dreams": dreams,
            "top_of_emotions": top_of_emotions,
            "top_of_symbols": top_of_symbols,
            "emotion_labels": [emotion.name for emotion in top_of_emotions],
            "emotion_data": [emotion.count for emotion in top_of_emotions],
            "symbol_labels": [symbol.name for symbol in top_of_symbols],
            "symbol_data": [symbol.count for symbol in top_of_symbols],
        }

        return render(
            request,
            "dream/dream_statistic.html",
            context=context
        )
