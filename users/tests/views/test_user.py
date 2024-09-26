import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from users.models import SIXTEEN_YEARS_IN_DAYS


class PublicUserTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="password",
            birth_date=datetime.date(1942, 2, 1)
        )
        self.user_detail_url = reverse(
            "users:user-detail",
            args=[str(self.user.id)]
        )
        self.user_create_url = reverse("users:user-create")

    def test_login_required_user_detail(self):
        response = self.client.get(self.user_detail_url)
        self.assertEqual(302, response.status_code)

    def test_user_create(self):
        username = "test_create"
        email = "new@mail.co"
        first_name = "First test"
        last_name = "Last_name"
        birth = datetime.date(2001, 3, 5)
        password = "hashed_PASS2456"
        response = self.client.post(
            self.user_create_url,
            data={
                "username": username,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "birth_date": birth.isoformat(),
                "password1": password,
                "password2": password,
            }
        )

        self.assertEqual(302, response.status_code)

        created_user = get_user_model().objects.last()
        self.assertEqual(created_user.username, username)
        self.assertEqual(created_user.email, email)
        self.assertEqual(created_user.first_name, first_name)
        self.assertEqual(created_user.last_name, last_name)
        self.assertEqual(created_user.birth_date, birth)
        self.assertTrue(created_user.check_password(password))

    def test_user_create_invalid_birth_date(self):
        username = "test_invalid_birth"
        email = "ttest@mail.co"
        first_name = "Firs test"
        last_name = "Lastname"
        birth = datetime.date(2009, 3, 5)
        password = "hashed_PASS2456"
        response = self.client.post(
            self.user_create_url,
            data={
                "username": username,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "birth_date": birth.isoformat(),
                "password1": password,
                "password2": password,
            }
        )

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "registration/register.html")
        self.assertContains(
            response,
            f"You must be older than {SIXTEEN_YEARS_IN_DAYS // 365}"
        )


class PrivateUserTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="user test",
            password="password3521",
            birth_date=datetime.date(1999, 6, 19)
        )
        self.client.force_login(self.user)
        self.user_detail_url = reverse(
            "users:user-detail",
            args=[str(self.user.id)]
        )

    def test_get_detail_user(self):
        response = self.client.get(self.user_detail_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.user, response.context["current_user"])
        self.assertEqual("", response.context["top_emotion"])
        self.assertEqual("", response.context["top_symbol"])
        self.assertTemplateUsed(response, "users/user_detail.html")

    def test_user_successful_delete(self):
        delete_url = reverse(
            "users:user-delete",
            args=[
                str(self.user.id),
            ]
        )
        response = self.client.delete(delete_url)
        self.assertEqual(302, response.status_code)
        self.assertEqual(0, get_user_model().objects.count())

    def test_user_trying_to_delete_another_user(self):
        hacker = get_user_model().objects.create_user(
            username="hacker",
            password="pass hasck",
            birth_date=datetime.date(2000, 2, 2)
        )
        self.client.force_login(hacker)
        delete_url = reverse(
            "users:user-delete",
            args=[
                str(self.user.id),
            ]
        )
        response = self.client.delete(delete_url,)
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            "You do not have permission to delete this user.",
            response.content.decode()
        )
