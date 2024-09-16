from django.contrib.auth.models import AbstractUser
from django.db import models


class Emotion(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name
