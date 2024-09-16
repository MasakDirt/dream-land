import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from users.models import Profile


class PublicProfileViewTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="new_user_username",
            password="passwordnew",
            birth_date=datetime.date(1956, 4, 25)
        )
        self.profile_create_url = reverse(
            "users:profile-create",
            args=[str(self.user.id)]
        )

        self.profile = Profile.objects.create(
            bio="New bio for new user",
            user=self.user
        )
        self.profile_update_url = reverse(
            "users:profile-update",
            args=[str(self.user.id), str(self.profile.id)]
        )

    def test_login_required_profile_create(self):
        response = self.client.get(self.profile_create_url)
        self.assertEqual(302, response.status_code)

    def test_login_required_profile_update(self):
        response = self.client.get(self.profile_update_url)
        self.assertEqual(302, response.status_code)


class PrivateProfileViewTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="new_user_for_profile",
            password="12489096756",
            birth_date=datetime.date(2004, 8, 11)
        )
        self.client.force_login(self.user)
        self.profile_create_url = reverse(
            "users:profile-create",
            args=[str(self.user.id)]
        )

    def test_get_create_profile_form(self):
        response = self.client.get(self.profile_create_url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "users/profile_form.html")

    def test_get_update_profile_form(self):
        user = get_user_model().objects.create_user(
            username="new_user_for_profile2",
            password="1248909675136",
            birth_date=datetime.date(2004, 8, 11)
        )
        profile = Profile.objects.create(
            bio="Bo",
            user=user
        )
        profile_update_url = reverse(
            "users:profile-update",
            args=[str(user.id), str(profile.id)]
        )
        response = self.client.get(profile_update_url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "users/profile_form.html")

    def test_create_profile(self):
        bio = "Users biography"
        response = self.client.post(
            self.profile_create_url,
            data={
                "bio": bio
            }
        )
        self.assertEqual(302, response.status_code)

        profile = Profile.objects.last()
        self.assertEqual(bio, profile.bio)

    def test_update_profile(self):
        user = get_user_model().objects.create_user(
            username="new_user_for_profile3",
            password="1248909675136",
            birth_date=datetime.date(2002, 3, 19)
        )
        profile = Profile.objects.create(
            bio="Biofile",
            user=user
        )
        profile_update_url = reverse(
            "users:profile-update",
            args=[str(user.id), str(profile.id)]
        )
        new_profile_bio = "New profile bio"
        response = self.client.post(
            profile_update_url,
            data={
                "bio": new_profile_bio,
            }
        )
        profile.refresh_from_db()
        self.assertEqual(302, response.status_code)
        self.assertEqual(new_profile_bio, profile.bio)
