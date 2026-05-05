import datetime

from django.contrib.auth import get_user_model
from django.db.models import Count, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from dto.dto import GraphicDto
from dream.models import Dream, Commentary, DreamLike, DreamDislike, CommentaryLike, CommentaryDislike


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


def additional_stats() -> dict:
    # Total likes and dislikes
    dream_likes_count = DreamLike.objects.count()
    dream_dislikes_count = DreamDislike.objects.count()
    commentary_likes_count = CommentaryLike.objects.count()
    commentary_dislikes_count = CommentaryDislike.objects.count()

    # Recent activity (last 7 days)
    seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    recent_dreams = Dream.objects.filter(date_recorded__gte=seven_days_ago).count()
    recent_commentaries = Commentary.objects.filter(created_time__gte=seven_days_ago).count()
    recent_users = get_user_model().objects.filter(date_joined__gte=seven_days_ago).count()

    # Most active user (by dreams)
    most_active_user = Dream.objects.values('user__username').annotate(dream_count=Count('user')).order_by('-dream_count').first()
    most_active_username = most_active_user['user__username'] if most_active_user else None
    most_active_count = most_active_user['dream_count'] if most_active_user else 0

    return {
        "dream_likes_count": dream_likes_count,
        "dream_dislikes_count": dream_dislikes_count,
        "commentary_likes_count": commentary_likes_count,
        "commentary_dislikes_count": commentary_dislikes_count,
        "recent_dreams": recent_dreams,
        "recent_commentaries": recent_commentaries,
        "recent_users": recent_users,
        "most_active_username": most_active_username,
        "most_active_count": most_active_count,
    }


def index(request: HttpRequest) -> HttpResponse:
    visit_count = request.session.get("visit_count", 0)
    request.session["visit_count"] = visit_count + 1

    visit_record = request.session.get("visit_record", 0)
    if visit_record < visit_count + 1:
        request.session["visit_record"] = visit_count + 1

    context = {
        "visit_count": visit_count + 1,
        "visit_record": request.session["visit_record"],
        **get_graphics(),
        **month_statistic_counter(),
        **additional_stats(),
    }

    return render(request, "dream/index.html", context=context)
