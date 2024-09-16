import datetime

from django.conf.global_settings import AUTH_USER_MODEL
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from users.models import Follow, Profile


class ModelTests(TestCase):
    @staticmethod
    def create_user(
            username: str = "Test user",
            password: str = "password1234",
            birth_date: datetime = datetime.date(1993, 2, 24),
            **kwargs
    ) -> AUTH_USER_MODEL:
        return get_user_model().objects.create_user(
            username=username,
            password=password,
            birth_date=birth_date,
            **kwargs
        )

    def test_success_user_birth_date_validation(self):
        birth_date = datetime.date(1999, 2, 15)
        user = get_user_model()(
            username="test",
            password="pass",
            birth_date=birth_date
        )
        user.full_clean()
        user.save()
        self.assertEqual(user.birth_date, birth_date)

    def test_incorrect_user_birth_date_validation(self):
        user = get_user_model()(
            username="test",
            password="pass",
            birth_date=datetime.date(2020, 9, 25)
        )
        with self.assertRaises(ValidationError):
            user.full_clean()
            user.save()

    def test_user_absolute_url(self):
        user = self.create_user(
            username="test",
            password="pass",
            birth_date=datetime.date(1999, 2, 15)
        )
        self.assertEqual(f"/users/{user.id}/", user.get_absolute_url())

    def test_profile_str_method(self):
        username = "test user"
        password = "pass"
        user = self.create_user(
            username=username,
            password=password,
            birth_date=datetime.date(2000, 12, 2)
        )
        profile = Profile.objects.create(
            bio="Smth about me",
            user=user,
        )
        self.assertEqual(f"{user.username} profile", str(profile))

    def test_if_following_true(self):
        follower = self.create_user(
            username="follower",
            password="password1245",
            birth_date=datetime.date(1999, 2, 15)
        )
        followed = self.create_user(
            username="followed",
            password="password54321",
            birth_date=datetime.date(1999, 9, 1)
        )
        Follow.objects.create(
            follower=follower,
            followed=followed
        )
        self.assertTrue(Follow.is_following(
            follower_user=follower,
            followed_user=followed
        ))

    def test_if_following_false(self):
        user_test = self.create_user(
            username="user_test",
            password="password1245",
            birth_date=datetime.date(2005, 12, 25)
        )
        another_user = self.create_user(
            username="another_user",
            password="password54321",
            birth_date=datetime.date(2002, 6, 11)
        )

        self.assertFalse(Follow.is_following(
            follower_user=user_test,
            followed_user=another_user
        ))
