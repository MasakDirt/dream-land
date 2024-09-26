import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from dream.models import Emotion


EMOTION_CREATE_URL = reverse("dream:emotion-create")


class PublicEmotionViewTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="user_test",
            password="password",
            birth_date=datetime.date(2000, 2, 12)
        )

    def test_login_required_symbol_create(self):
        response = self.client.get(EMOTION_CREATE_URL)
        self.assertEqual(302, response.status_code)


class PrivateSymbolViewTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="username",
            password="password1245",
            birth_date=datetime.date(1900, 12, 2)
        )
        self.client.force_login(self.user)

    def test_get_emotion_create(self):
        response = self.client.get(EMOTION_CREATE_URL)
        self.assertTemplateUsed(response, "dream/emotion_form.html")

    def test_create_symbol(self):
        name = "Test emotion"
        description = "Some description of emotion"
        response = self.client.post(
            EMOTION_CREATE_URL,
            data={
                "name": name,
                "description": description
            }
        )

        self.assertEqual(302, response.status_code)

        emotion = Emotion.objects.last()
        self.assertEqual(emotion.name, name)
        self.assertEqual(emotion.description, description)
