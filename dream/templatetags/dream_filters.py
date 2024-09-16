from django import template
from django.conf.global_settings import AUTH_USER_MODEL

from dream.models import DreamLike, Dream, DreamDislike

register = template.Library()


@register.filter
def is_authorized_user_liked(dream: Dream, user: AUTH_USER_MODEL):
    return DreamLike.is_user_liked(owner=user, dream=dream)


@register.filter
def is_authorized_user_disliked(dream: Dream, user: AUTH_USER_MODEL):
    return DreamDislike.is_user_disliked(owner=user, dream=dream)
