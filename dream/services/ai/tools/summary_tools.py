from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import (
    Count,
)
from pydantic import BaseModel, Field

from dto.dto import EmotionDto, SymbolDto


class UserStatisticParams(BaseModel):
    """User statistic parameters for AI agent"""
    user_pk: int | str = Field(description="You should paste there user pk to get detailed statistic!")


def get_user_statistic(params: UserStatisticParams) -> dict[str, Any]:
    user = get_user_model().objects.prefetch_related(
        "dreams__emotions",
        "dreams__symbols",
    ).get(pk=params.user_pk)

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

    return {
        "current_user": {
            "id": user.id,
            "username": user.username,
        },
        "count_dreams": dreams.count(),
        "dreams": [
            {
                "id": d.id,
                "title": d.title,
                "date_recorded": d.date_recorded.isoformat() if d.date_recorded else None,
            }
            for d in dreams[:20]
        ],
        "top_of_emotions": [
            {
                "name": e.name,
                "count": e.count,
            }
            for e in top_of_emotions
        ],
        "top_of_symbols": [
            {
                "name": s.name,
                "count": s.count,
            }
            for s in top_of_symbols
        ],
        "emotion_labels": [e.name for e in top_of_emotions],
        "emotion_data": [e.count for e in top_of_emotions],
        "symbol_labels": [s.name for s in top_of_symbols],
        "symbol_data": [s.count for s in top_of_symbols],
    }
