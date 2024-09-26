import datetime

from django.conf.global_settings import AUTH_USER_MODEL
from django.contrib.auth import get_user_model
from django.test import TestCase

from dream.models import (
    Emotion,
    Symbol,
    Dream,
    DreamLike,
    DreamDislike,
    Commentary,
    CommentaryLike,
    CommentaryDislike,
)


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

    @staticmethod
    def create_dream(
            title: str = "Test title",
            description: str = "Description for test dream!"
    ) -> Dream:
        return Dream.objects.create(
            title=title,
            description=description,
            user=ModelTests.create_user()
        )

    @staticmethod
    def create_commentary(
            owner: AUTH_USER_MODEL,
            dream: Dream,
            content: str = "New content for comment"
    ) -> Commentary:
        return Commentary.objects.create(
            owner=owner,
            dream=dream,
            content=content,
        )

    def test_emotion_str(self):
        name = "emotion"
        emotion = Emotion.objects.create(
            name=name,
            description="some_descr",
        )
        self.assertEqual(name, str(emotion))

    def test_symbol_str(self):
        name = "symbol_test"
        symbol = Symbol.objects.create(
            name=name,
            description="some_descr",
        )
        self.assertEqual(name, str(symbol))

    def test_dream_str(self):
        title = "Test title"
        description = """Test movie description, 
        it`s about some test thing, that I try to include"""
        dream = Dream.objects.create(
            title=title,
            description=description,
            user=self.create_user()
        )
        self.assertEqual(f"{title} ({description[:33]}...)", str(dream))

    def test_dream_absolute_url(self):
        dream = self.create_dream()
        self.assertEqual(
            f"/users/{dream.user.id}/dreams/{dream.pk}/",
            dream.get_absolute_url(),
        )

    def test_dream_like_is_user_liked_true(self):
        like_owner = self.create_user(username="new user")
        liked_dream = self.create_dream()
        DreamLike.objects.create(
            owner=like_owner,
            dream=liked_dream
        )
        self.assertTrue(DreamLike.is_user_liked(
            owner=like_owner,
            dream=liked_dream
        ))

    def test_dream_like_is_user_liked_false(self):
        user = self.create_user(username="user not liked")
        dream = self.create_dream(title="Unliked dream")
        self.assertFalse(DreamLike.is_user_liked(
            owner=user,
            dream=dream
        ))

    def test_dream_dislike_is_user_disliked_true(self):
        dislike_owner = self.create_user(username="disliked dream user")
        disliked_dream = self.create_dream()
        DreamDislike.objects.create(
            owner=dislike_owner,
            dream=disliked_dream
        )
        self.assertTrue(DreamDislike.is_user_disliked(
            owner=dislike_owner,
            dream=disliked_dream
        ))

    def test_dream_dislike_is_user_disliked_false(self):
        user = self.create_user(username="user not disliked")
        dream = self.create_dream(title="Unliked dream")
        self.assertFalse(DreamDislike.is_user_disliked(
            owner=user,
            dream=dream
        ))

    def test_commentary_str(self):
        username = "commentary owner"
        content = "It`s a commentary content!"
        commentary = Commentary.objects.create(
            owner=self.create_user(username=username),
            dream=self.create_dream(),
            content=content
        )
        self.assertEqual(
            f"'{username}' writes [{content[:50]}...]",
            str(commentary)
        )

    def test_commentary_like_is_user_liked_true(self):
        like_owner = self.create_user(username="comment like")
        commentary = self.create_commentary(
            owner=self.create_user(username="new commentary owner"),
            dream=self.create_dream(),
        )
        CommentaryLike.objects.create(
            owner=like_owner,
            commentary=commentary
        )
        self.assertTrue(CommentaryLike.is_user_liked(
            owner=like_owner,
            commentary=commentary
        ))

    def test_commentary_like_is_user_liked_false(self):
        user = self.create_user(username="usual user")
        commentary = self.create_commentary(
            owner=self.create_user(username="new commentary owner2"),
            dream=self.create_dream(),
        )
        self.assertFalse(CommentaryLike.is_user_liked(
            owner=user,
            commentary=commentary
        ))

    def test_commentary_dislike_is_user_disliked_true(self):
        dislike_owner = self.create_user(username="comment dislike")
        commentary = self.create_commentary(
            owner=self.create_user(username="new commentary owner3"),
            dream=self.create_dream(),
        )
        CommentaryDislike.objects.create(
            owner=dislike_owner,
            commentary=commentary
        )
        self.assertTrue(CommentaryDislike.is_user_disliked(
            owner=dislike_owner,
            commentary=commentary
        ))

    def test_commentary_dislike_is_user_disliked_false(self):
        dislike_owner = self.create_user(username="comment dislike1")
        commentary = self.create_commentary(
            owner=self.create_user(username="new commentary owner4"),
            dream=self.create_dream(),
        )
        self.assertFalse(CommentaryDislike.is_user_disliked(
            owner=dislike_owner,
            commentary=commentary
        ))
