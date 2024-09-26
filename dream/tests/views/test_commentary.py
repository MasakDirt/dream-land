import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from dream.models import Dream, Commentary, CommentaryLike, CommentaryDislike


class PublicCommentaryViewsTest(TestCase):
    def setUp(self):
        self.stasik = get_user_model().objects.create_user(
            username="stasik",
            password="pass",
            birth_date=datetime.date(2000, 12, 1)
        )
        self.sergey = get_user_model().objects.create_user(
            username="sergey",
            password="pass",
            birth_date=datetime.date(2000, 12, 1)
        )
        self.stasik_dream = Dream.objects.create(
            title="Stasik dream",
            description="Stasik description",
            user=self.stasik,
        )
        self.comment = Commentary.objects.create(
            owner=self.sergey,
            dream=self.stasik_dream,
            content="Nice dream"
        )

    def test_login_required_commentary_add_remove_like(self):
        url = reverse(
            "dream:comment-like",
            args=[
                str(self.stasik.id),
                str(self.stasik_dream.id),
                str(self.comment.id)
            ]
        )
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.assertFalse(
            CommentaryLike.is_user_liked(self.sergey, self.comment))

    def test_login_required_commentary_add_remove_dislike(self):
        url = reverse(
            "dream:comment-dislike",
            args=[
                str(self.stasik.id),
                str(self.stasik_dream.id),
                str(self.comment.id)
            ]
        )
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)

    def test_login_required_commentary_create(self):
        url = reverse(
            "dream:commentary-create",
            args=[
                str(self.stasik.id),
                str(self.stasik_dream.id)
            ]
        )
        response = self.client.post(
            url,
            data={
                "content": "I like it post!"
            }
        )
        self.assertEqual(302, response.status_code)

    def test_login_required_commentary_delete(self):
        url = reverse(
            "dream:commentary-delete",
            args=[
                str(self.stasik.id),
                str(self.stasik_dream.id),
                str(self.sergey.id)
            ]
        )
        response = self.client.delete(url)
        self.assertEqual(302, response.status_code)


class PrivateCommentaryViewsTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="new_user",
            password="password",
            birth_date=datetime.date(1946, 4, 2)
        )
        self.client.force_login(self.user)

        self.user_with_dream = get_user_model().objects.create_user(
            username="user_with_dream",
            password="password1234355",
            birth_date=datetime.date(1987, 2, 23)
        )
        self.dream = Dream.objects.create(
            title="Users dream",
            description="Users description",
            user=self.user_with_dream,
        )
        self.comment = Commentary.objects.create(
            owner=self.user,
            dream=self.dream,
            content="Nice dream"
        )

    def test_comment_add_like_and_remove_it(self):
        comment_add_remove_like_url = reverse(
            "dream:comment-like",
            args=[
                str(self.user_with_dream.id),
                str(self.dream.id),
                str(self.comment.id)
            ]
        )
        add_response = self.client.post(comment_add_remove_like_url)

        self.assertEqual(302, add_response.status_code)
        self.assertTrue(CommentaryLike.is_user_liked(self.user, self.comment))

        remove_response = self.client.post(comment_add_remove_like_url)

        self.assertEqual(302, remove_response.status_code)
        self.assertFalse(CommentaryLike.is_user_liked(self.user, self.comment))

    def test_comment_add_dislike_and_remove_it(self):
        comment_add_remove_dislike_url = reverse(
            "dream:comment-dislike",
            args=[
                str(self.user_with_dream.id),
                str(self.dream.id),
                str(self.comment.id)
            ]
        )

        add_response = self.client.post(comment_add_remove_dislike_url)

        self.assertEqual(302, add_response.status_code)
        self.assertTrue(CommentaryDislike.is_user_disliked(
            self.user,
            self.comment
        ))

        remove_response = self.client.post(comment_add_remove_dislike_url)

        self.assertEqual(302, remove_response.status_code)
        self.assertFalse(CommentaryDislike.is_user_disliked(
            self.user,
            self.comment
        ))

    def test_commentary_create(self):
        url = reverse(
            "dream:commentary-create",
            args=[
                str(self.user_with_dream.id),
                str(self.dream.id)
            ]
        )
        content = "I like it post!"
        response = self.client.post(
            url,
            data={
                "content": content
            }
        )
        self.assertEqual(302, response.status_code)
        self.assertTrue(
            self.dream.commentaries.filter(content=content).exists()
        )
        comment = self.dream.commentaries.filter(content=content).first()
        self.assertEqual(self.user, comment.owner)

    def test_commentary_successful_delete(self):
        delete_url = reverse(
            "dream:commentary-delete",
            args=[
                str(self.user_with_dream.id),
                str(self.dream.id),
                str(self.comment.id)
            ]
        )
        response = self.client.delete(delete_url)
        self.assertEqual(302, response.status_code)
        self.assertEqual(0, self.dream.commentaries.count())

    def test_commentary_trying_to_delete_another_user(self):
        self.client.force_login(self.user_with_dream)
        delete_url = reverse(
            "dream:commentary-delete",
            args=[
                str(self.user_with_dream.id),
                str(self.dream.id),
                str(self.comment.id)
            ]
        )
        response = self.client.delete(delete_url,)
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            "You do not have permission to delete this commentary.",
            response.content.decode()
        )
