import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponse
from django.urls import reverse


SIXTEEN_YEARS_IN_DAYS = 5844


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

