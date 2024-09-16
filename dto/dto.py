from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

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


@dataclass
class GraphicDto:
    labels: list
    data: list

    @staticmethod
    def _get_count(query_set: QuerySet[dict]) -> list[int]:
        return [item["count"] for item in query_set]

    @classmethod
    def get_from_query_set(
            cls, query_set: QuerySet[dict],
            get_labels_func: Callable
    ) -> GraphicDto:
        return cls(
            get_labels_func(query_set),
            cls._get_count(query_set)
        )


@dataclass
class SymbolDto:
    name: str
    count: int
    description: str

    @classmethod
    def get_from_query_set(cls, data: QuerySet[dict]) -> list[SymbolDto]:
        return [
            cls(
                symbol["symbols__name"],
                symbol["total_count"],
                symbol["symbols__description"]
            )
            for symbol in data
        ]


@dataclass
class EmotionDto:
    name: str
    count: int
    description: str

    @classmethod
    def get_from_query_set(cls, data: QuerySet[dict]) -> list[EmotionDto]:
        return [
            cls(
                emotion["emotions__name"],
                emotion["total_count"],
                emotion["emotions__description"]
            )
            for emotion in data
        ]
