from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from django.conf.global_settings import AUTH_USER_MODEL
from django.db.models import QuerySet

from dream.models import DreamLike, DreamDislike, Commentary, Dream


@dataclass
class DreamListDto:
    id: int
    pk: int
    title: str
    description: str
    is_visited: bool
    user: AUTH_USER_MODEL
    date_recorded: datetime
    likes: QuerySet[DreamLike]
    dislikes: QuerySet[DreamDislike]
    commentaries: QuerySet[Commentary]

    @classmethod
    def get_from_dream(cls, dream: Dream, is_visited: bool) -> DreamListDto:
        return cls(
            id=dream.id,
            pk=dream.pk,
            title=dream.title,
            description=dream.description,
            is_visited=is_visited,
            user=dream.user,
            date_recorded=dream.date_recorded,
            likes=dream.likes.all(),
            dislikes=dream.dislikes.all(),
            commentaries=dream.commentaries.all(),
        )
