from django import template

from users.models import User, Follow

register = template.Library()


@register.filter
def is_following(follower_user: User, followed_user: User) -> bool:
    return Follow.is_following(
        follower_user=follower_user,
        followed_user=followed_user
    )
