from datetime import datetime
from typing import Any

from django.db.models import Count
from pydantic import BaseModel, Field

from dream.models import Dream, Emotion, Symbol
from users.models import User


class UserEmotionsParams(BaseModel):
    name: str = Field(description="Name of emotion, for example: 'Happy', 'Sad', 'Angry' etc.")


class UserSymbolsParams(BaseModel):
    name: str = Field(description="Name of symbol, for example: 'Water', 'Fire', 'Tree' etc.")


class UserDreamsParams(BaseModel):
    """User dreams params for chat agent"""
    user_pk: int | str = Field(description="You should add there user PK, to get dreams of this user.")
    emotions: list[UserEmotionsParams] | None = Field(
        None, description="List of emotions associated with this user's dreams."
    )
    symbols: list[UserSymbolsParams] | None = Field(
        None, description="List of symbols associated with this user's dreams."
    )
    date_recorded_gte: datetime | None = Field(
        None, description="Date recorded for this user's dreams (from date)."
    )
    date_recorded_lte: datetime | None = Field(
        None, description="Date recorded for this user's dreams (to date)."
    )
    likes_count_gte: int | None = Field(None, description="Minimum number of likes on the dream.")
    likes_count_lte: int | None = Field(None, description="Maximum number of likes on the dream.")
    dislikes_count_gte: int | None = Field(None, description="Minimum number of dislikes on the dream.")
    dislikes_count_lte: int | None = Field(None, description="Maximum number of dislikes on the dream.")
    comments_count_gte: int | None = Field(None, description="Minimum number of comments on the dream.")
    comments_count_lte: int | None = Field(None, description="Maximum number of comments on the dream.")


class UserEmotionsFiltersParams(BaseModel):
    """Get all emotions for user's dreams"""
    user_pk: int | str = Field(description="User PK to get all emotions from their dreams.")


class UserSymbolsFiltersParams(BaseModel):
    """Get all symbols for user's dreams"""
    user_pk: int | str = Field(description="User PK to get all symbols from their dreams.")


class UserSubscribersParams(BaseModel):
    """Get all subscribers (followers) of a user"""
    user_pk: int | str = Field(description="User PK to get all subscribers/followers of this user.")


def get_user_dreams(params: UserDreamsParams) -> dict[str, Any]:
    """Get user dreams with detailed filtering by emotions, symbols, likes, dislikes, comments and date range."""
    dreams_qs = Dream.objects.prefetch_related(
        "emotions",
        "symbols",
        "user",
        "likes",
        "dislikes",
        "commentaries"
    ).filter(user_id=params.user_pk).annotate(
        likes_count=Count("likes"),
        dislikes_count=Count("dislikes"),
        comments_count=Count("commentaries")
    )

    # Filter by emotions
    if params.emotions:
        emotion_names = [emotion.name for emotion in params.emotions]
        dreams_qs = dreams_qs.filter(emotions__name__in=emotion_names).distinct()

    # Filter by symbols
    if params.symbols:
        symbol_names = [symbol.name for symbol in params.symbols]
        dreams_qs = dreams_qs.filter(symbols__name__in=symbol_names).distinct()

    # Filter by date range
    if params.date_recorded_gte:
        dreams_qs = dreams_qs.filter(date_recorded__gte=params.date_recorded_gte)
    if params.date_recorded_lte:
        dreams_qs = dreams_qs.filter(date_recorded__lte=params.date_recorded_lte)

    # Filter by likes count
    if params.likes_count_gte is not None:
        dreams_qs = dreams_qs.filter(likes_count__gte=params.likes_count_gte)
    if params.likes_count_lte is not None:
        dreams_qs = dreams_qs.filter(likes_count__lte=params.likes_count_lte)

    # Filter by dislikes count
    if params.dislikes_count_gte is not None:
        dreams_qs = dreams_qs.filter(dislikes_count__gte=params.dislikes_count_gte)
    if params.dislikes_count_lte is not None:
        dreams_qs = dreams_qs.filter(dislikes_count__lte=params.dislikes_count_lte)

    # Filter by comments count
    if params.comments_count_gte is not None:
        dreams_qs = dreams_qs.filter(comments_count__gte=params.comments_count_gte)
    if params.comments_count_lte is not None:
        dreams_qs = dreams_qs.filter(comments_count__lte=params.comments_count_lte)

    return {
        "dreams": [
            {
                "id": dream.id,
                "title": dream.title,
                "description": dream.description,
                "date_recorded": dream.date_recorded.isoformat(),
                "likes_count": dream.likes_count,
                "dislikes_count": dream.dislikes_count,
                "comments_count": dream.comments_count,
                "emotions": list(dream.emotions.values_list("name", flat=True)),
                "symbols": list(dream.symbols.values_list("name", flat=True)),
            }
            for dream in dreams_qs
        ]
    }


def get_user_emotions(params: UserEmotionsFiltersParams) -> dict[str, Any]:
    """Get all unique emotions associated with a user's dreams."""
    emotions = Emotion.objects.filter(
        dreams__user_id=params.user_pk
    ).distinct().values("id", "name", "description")

    return {
        "emotions": list(emotions),
        "total_count": len(list(emotions))
    }


def get_user_symbols(params: UserSymbolsFiltersParams) -> dict[str, Any]:
    """Get all unique symbols associated with a user's dreams."""
    symbols = Symbol.objects.filter(
        dreams__user_id=params.user_pk
    ).distinct().values("id", "name", "description")

    return {
        "symbols": list(symbols),
        "total_count": len(list(symbols))
    }


def get_user_subscribers(params: UserSubscribersParams) -> dict[str, Any]:
    """Get all subscribers (followers) of a specific user."""
    try:
        user = User.objects.get(pk=params.user_pk)
    except User.DoesNotExist:
        return {"subscribers": [], "total_count": 0}

    followers = user.followers.all().values(
        "follower__id",
        "follower__username",
        "follower__first_name",
        "follower__last_name",
        "created_time"
    )

    # Convert datetime objects to ISO format strings
    followers_list = [
        {
            **follower,
            "created_time": follower["created_time"].isoformat()
        }
        for follower in followers
    ]

    return {
        "subscribers": followers_list,
        "total_count": user.followers.count()
    }
