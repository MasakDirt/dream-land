from django.contrib.auth.models import AbstractUser
from django.db import models
from django.http import HttpResponse
from django.urls import reverse

from django.conf import settings


class Emotion(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Symbol(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Dream(models.Model):
    title = models.CharField(max_length=125)
    description = models.TextField(null=True, blank=True)
    date_recorded = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dreams"
    )
    symbols = models.ManyToManyField(Symbol, related_name="dreams")
    emotions = models.ManyToManyField(Emotion, related_name="dreams")

    class Meta:
        ordering = ("-date_recorded",)

    def __str__(self) -> str:
        return f"{self.title} ({self.description[:33]}...)"

    def get_absolute_url(self) -> HttpResponse:
        return reverse("dream:dream-detail", kwargs={
            "user_pk": str(self.user.id),
            "pk": str(self.pk),
        })
