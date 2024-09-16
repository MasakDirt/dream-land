from django import template
from django.conf.global_settings import AUTH_USER_MODEL

from dream.models import CommentaryLike, Commentary, CommentaryDislike

register = template.Library()


@register.filter
def is_user_liked(commentary: Commentary, user: AUTH_USER_MODEL):
    return CommentaryLike.is_user_liked(owner=user, commentary=commentary)


@register.filter
def is_user_disliked(commentary: Commentary, user: AUTH_USER_MODEL):
    return CommentaryDislike.is_user_disliked(
        owner=user,
        commentary=commentary
    )
