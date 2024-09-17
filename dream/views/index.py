import datetime

from django.contrib.auth import get_user_model
from django.db.models import Count, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from dto.dto import GraphicDto
from dream.models import Dream, Commentary


VISIT_RECORD = 0


def get_dream_labels(query_set: QuerySet[dict]) -> list[str]:
    return [
        f"{datetime.date(
            item["date_recorded__year"],
            item["date_recorded__month"],
            1
        ).strftime("%B %y")}"
        for item in query_set
    ]


def get_emotion_labels(query_set: QuerySet[dict]) -> list[str]:
    return [item["emotions__name"] for item in query_set]


def get_graphics() -> dict:
    dream_graphic_per_month = GraphicDto.get_from_query_set(
        Dream.objects.values(
            "date_recorded__month",
            "date_recorded__year"
        ).annotate(count=Count("title")).order_by(
            "date_recorded__year",
            "date_recorded__month"
        ),
        get_dream_labels
    )
    top_emotions_graphic = GraphicDto.get_from_query_set(
        Dream.objects.values("emotions__name")
        .annotate(count=Count("title")).order_by("-count")[:10],
        get_emotion_labels
    )

    return {
        "dream_graphic": dream_graphic_per_month,
        "emotions_graphic": top_emotions_graphic,
    }


def month_statistic_counter() -> dict:
    month_today = datetime.date.today().month
    year_today = datetime.date.today().year

    profiles_count = get_user_model().objects.count()
    profiles_month_count = get_user_model().objects.filter(
        date_joined__month=month_today,
        date_joined__year=year_today
    ).count()

    dreams_count = Dream.objects.count()
    dreams_month_count = Dream.objects.filter(
        date_recorded__month=month_today,
        date_recorded__year=year_today
    ).count()

    commentary_count = Commentary.objects.count()
    commentary_month_count = Commentary.objects.filter(
        created_time__month=month_today,
        created_time__year=year_today
    ).count()

    return {
        "profiles_count": profiles_count,
        "dreams_count": dreams_count,
        "commentary_count": commentary_count,
        "profiles_month_count": profiles_month_count,
        "dreams_month_count": dreams_month_count,
        "commentary_month_count": commentary_month_count,
    }


def index(request: HttpRequest) -> HttpResponse:
    global VISIT_RECORD

    visit_count = request.session.get("visit_count", 0)
    request.session["visit_count"] = visit_count + 1
    if VISIT_RECORD < visit_count + 1:
        VISIT_RECORD = visit_count + 1

    context = {
        "visit_count": visit_count + 1,
        "visit_record": VISIT_RECORD,
        **get_graphics(),
        **month_statistic_counter(),
    }

    return render(request, "dream/index.html", context=context)
