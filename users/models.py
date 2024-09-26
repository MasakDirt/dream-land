import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponse
from django.urls import reverse


SIXTEEN_YEARS_IN_DAYS = 12 * 365 + 4 * 366


def validate_birth_date(birth_date):
    difference = datetime.date.today() - datetime.timedelta(
        days=SIXTEEN_YEARS_IN_DAYS
    )
    if birth_date > difference:
        raise ValidationError(
            f"You must be older than {SIXTEEN_YEARS_IN_DAYS // 365}"
        )


class User(AbstractUser):
    birth_date = models.DateField(validators=[validate_birth_date])

    def get_absolute_url(self) -> HttpResponse:
        return reverse("users:user-detail", kwargs={"pk": str(self.pk)})


class Profile(models.Model):
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        null=True,
        blank=True
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.user.username} profile"


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following"
    )
    followed = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers"
    )
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "followed")
        ordering = ("-created_time",)

    @staticmethod
    def is_following(
            follower_user: settings.AUTH_USER_MODEL,
            followed_user: settings.AUTH_USER_MODEL
    ) -> bool:
        return Follow.objects.filter(
            follower=follower_user,
            followed=followed_user
        ).exists()
