from django.conf import settings
from django.db import models
from django.http import HttpResponse
from django.urls import reverse


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


class DreamLike(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dream_likes"
    )
    dream = models.ForeignKey(
        Dream,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("owner", "dream")

    @staticmethod
    def is_user_liked(owner: settings.AUTH_USER_MODEL, dream: Dream) -> bool:
        return DreamLike.objects.filter(
            owner=owner,
            dream_id=dream.id
        ).exists()


class DreamDislike(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dream_dislikes"
    )
    dream = models.ForeignKey(
        Dream,
        on_delete=models.CASCADE,
        related_name="dislikes"
    )
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("owner", "dream")

    @staticmethod
    def is_user_disliked(
            owner: settings.AUTH_USER_MODEL,
            dream: Dream
    ) -> bool:
        return DreamDislike.objects.filter(
            owner=owner,
            dream_id=dream.id
        ).exists()


class Commentary(models.Model):
    content = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="commentaries"
    )
    dream = models.ForeignKey(
        Dream,
        on_delete=models.CASCADE,
        related_name="commentaries"
    )
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Commentaries"
        ordering = ("-created_time",)

    def __str__(self) -> str:
        return f"'{self.owner.username}' writes [{self.content[:50]}...]"


class CommentaryLike(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="commentary_likes"
    )
    commentary = models.ForeignKey(
        Commentary,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("owner", "commentary")

    @staticmethod
    def is_user_liked(
            owner: settings.AUTH_USER_MODEL,
            commentary: Commentary
    ) -> bool:
        return CommentaryLike.objects.filter(
            owner=owner,
            commentary=commentary
        ).exists()


class CommentaryDislike(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="commentary_dislikes"
    )
    commentary = models.ForeignKey(
        Commentary,
        on_delete=models.CASCADE,
        related_name="dislikes"
    )
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("owner", "commentary")

    @staticmethod
    def is_user_disliked(
            owner: settings.AUTH_USER_MODEL,
            commentary: Commentary
    ) -> bool:
        return CommentaryDislike.objects.filter(
            owner=owner,
            commentary=commentary
        ).exists()
