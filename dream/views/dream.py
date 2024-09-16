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
from django.http import HttpRequest, HttpResponse
from django.views.generic import (
    ListView, DetailView
)

from dream.forms import DreamFilterForm, DreamSearchForm, CommentaryForm
from dream.models import Dream
from dto.dto import DreamListDto


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
            Dream.objects.select_related("user")
            .prefetch_related(
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
            "commentaries",
            "commentaries__owner",
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
