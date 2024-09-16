import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from dream.models import Symbol

SYMBOL_CREATE_URL = reverse("dream:symbol-create")


class PublicSymbolViewTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="user",
            password="pass",
            birth_date=datetime.date(2000, 2, 12)
        )

    def test_login_required_symbol_create(self):
        response = self.client.get(SYMBOL_CREATE_URL)
        self.assertEqual(302, response.status_code)


class PrivateSymbolViewTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="user",
            password="pass",
            birth_date=datetime.date(2000, 2, 12)
        )
        self.client.force_login(self.user)

    def test_get_symbol_create(self):
        response = self.client.get(SYMBOL_CREATE_URL)
        self.assertTemplateUsed(response, "dream/symbol_form.html")

    def test_create_symbol(self):
        name = "Test symbol"
        description = "Some description of symbol"
        response = self.client.post(
            SYMBOL_CREATE_URL,
            data={
                "name": name,
                "description": description
            }
        )

        self.assertEqual(302, response.status_code)

        symbol = Symbol.objects.last()
        self.assertEqual(symbol.name, name)
        self.assertEqual(symbol.description, description)
