import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from users.models import Follow


class PublicFollowViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="username test",
            password="password",
            birth_date=datetime.date(1990, 12, 2)
        )

    def test_login_required_follow(self):
        follower = get_user_model().objects.create_user(
            username="follower",
            password="fl23",
            birth_date=datetime.date(2001, 2, 12)
        )
        response = self.client.post(
            reverse(
                "users:user-follow",
                args=[str(self.user.id), str(follower.id)]
            )
        )
        self.assertEqual(302, response.status_code)

    def test_login_required_follower_list(self):
        response = self.client.post(
            reverse(
                "users:user-followers",
                args=[str(self.user.id)]
            )
        )
        self.assertEqual(302, response.status_code)

    def test_login_required_followed_list(self):
        response = self.client.post(
            reverse(
                "users:user-followed",
                args=[str(self.user.id)]
            )
        )
        self.assertEqual(302, response.status_code)


class PrivateFollowViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="username test",
            password="password",
            birth_date=datetime.date(1990, 12, 2)
        )
        self.client.force_login(self.user)

    def test_follow_create(self):
        follower = get_user_model().objects.create_user(
            username="follower_for_user",
            password="lajio245",
            birth_date=datetime.date(2003, 8, 25)
        )
        response = self.client.post(
            reverse(
                "users:user-follow",
                kwargs={
                    "followed_pk": str(self.user.id),
                    "follower_pk": str(follower.id)
                }
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertTrue(Follow.is_following(
            follower_user=follower,
            followed_user=self.user
        ))

    def test_follow_delete(self):
        follower = get_user_model().objects.create_user(
            username="follower_for_user_for_deleting",
            password="lajio245",
            birth_date=datetime.date(2003, 8, 25)
        )
        Follow.objects.create(
            follower=follower,
            followed=self.user
        )
        response = self.client.post(
            reverse(
                "users:user-follow",
                kwargs={
                    "followed_pk": str(self.user.id),
                    "follower_pk": str(follower.id)
                }
            )
        )
        self.assertEqual(302, response.status_code)
        self.assertFalse(Follow.is_following(
            follower_user=follower,
            followed_user=self.user
        ))

    def test_follower_list(self):
        follower = get_user_model().objects.create_user(
            username="follower_user",
            password="lajio245",
            birth_date=datetime.date(2003, 8, 25)
        )
        Follow.objects.create(
            follower=follower,
            followed=self.user
        )
        url = reverse("users:user-followers", args=[str(self.user.id)])
        response = self.client.get(url)
        self.assertTemplateUsed(response, "users/followers_list.html")
        self.assertContains(response, follower.username)
        self.assertContains(response, follower.dreams.count())
        self.assertContains(response, follower.dream_likes.count())
        self.assertContains(response, follower.dream_dislikes.count())

    def test_followed_list(self):
        followed = get_user_model().objects.create_user(
            username="followed_user",
            password="lajio245",
            birth_date=datetime.date(2003, 8, 25)
        )
        Follow.objects.create(
            follower=self.user,
            followed=followed
        )
        url = reverse("users:user-followed", args=[str(self.user.id)])
        response = self.client.get(url)
        self.assertTemplateUsed(response, "users/following_list.html")
        self.assertContains(response, followed.username)
        self.assertContains(response, followed.dreams.count())
        self.assertContains(response, followed.dream_likes.count())
        self.assertContains(response, followed.dream_dislikes.count())
