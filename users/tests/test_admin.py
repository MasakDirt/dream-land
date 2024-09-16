import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


class AdminTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = get_user_model().objects.create_superuser(
            username="admin user",
            password="password admin1235678575568",
            birth_date=datetime.date(2007, 12, 15)
        )
        self.client.force_login(self.admin)
        self.anatoly = get_user_model().objects.create_superuser(
            username="anatoly",
            password="sorokavorona35423",
            birth_date=datetime.date(2005, 8, 1)
        )

    def test_user_birth_date_listed(self):
        url = reverse("admin:users_user_changelist")
        response = self.client.get(url)
        self.assertContains(response, "birth_date")
        self.assertContains(
            response,
            self.anatoly.birth_date.strftime("%b. %d, %Y").replace(" 0", " ")
        )

    def test_user_detail_birth_date_listed(self):
        url = reverse("admin:users_user_change", args=[self.anatoly.id])
        response = self.client.get(url)
        self.assertContains(response, "birth_date")
        self.assertContains(response, self.anatoly.birth_date)

    def test_user_birth_date_create_listed(self):
        url = reverse("admin:users_user_add")
        response = self.client.get(url)
        self.assertContains(response, "birth_date")
