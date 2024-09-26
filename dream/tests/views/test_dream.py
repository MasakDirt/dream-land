import datetime

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.test import TestCase
from django.urls import reverse

from dto.dto import EmotionDto, SymbolDto
from dream.models import Dream, DreamLike, DreamDislike, Emotion, Symbol


DREAM_LIST_URL = reverse("dream:dream-list")


class PublicDreamViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user",
            password="pass",
            birth_date=datetime.date(1999, 9, 9)
        )
        self.dream = Dream.objects.create(
            title="Dream",
            description="Dream content",
            user=self.user
        )

    def test_login_required_dream_list(self):
        url = DREAM_LIST_URL
        response = self.client.get(url)

        self.assertEqual(302, response.status_code)

    def test_login_required_dream_detail(self):
        url = reverse(
            "dream:dream-detail",
            args=[str(self.user.pk), str(self.dream.pk)]
        )
        response = self.client.get(url)

        self.assertEqual(302, response.status_code)

    def test_login_required_dream_create(self):
        url = reverse(
            "dream:dream-create",
            args=[str(self.user.pk)]
        )
        response = self.client.post(
            url,
            data={
                "title": "title",
                "description": "description"
            }
        )

        self.assertEqual(302, response.status_code)

    def test_login_required_dream_update(self):
        url = reverse(
            "dream:dream-update",
            args=[str(self.user.pk), str(self.dream.pk)]
        )
        response = self.client.put(
            url,
            data={
                "title": "title",
                "description": "description"
            }
        )

        self.assertEqual(302, response.status_code)

    def test_login_required_dream_delete(self):
        url = reverse(
            "dream:dream-delete",
            args=[str(self.user.pk), str(self.dream.pk)]
        )
        response = self.client.delete(url)

        self.assertEqual(302, response.status_code)

    def test_login_required_dream_add_remove_like(self):
        url = reverse(
            "dream:dream-like",
            args=[str(self.user.pk), str(self.dream.pk)]
        )
        response = self.client.post(url)

        self.assertEqual(302, response.status_code)

    def test_login_required_dream_add_remove_dislike(self):
        url = reverse(
            "dream:dream-dislike",
            args=[str(self.user.pk), str(self.dream.pk)]
        )
        response = self.client.post(url)

        self.assertEqual(302, response.status_code)

    def test_login_required_dreams_detailed_statistic(self):
        url = reverse(
            "dream:user-dream-statistic",
            args=[str(self.user.pk)]
        )
        response = self.client.get(url)

        self.assertEqual(302, response.status_code)


class PrivateDreamViewsTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="new_user",
            password="new_pass",
            birth_date=datetime.date(2085, 9, 9)
        )
        self.client.force_login(self.user
                                )
        Dream.objects.create(
            title="First dream",
            description="First description",
            user=self.user
        )
        Dream.objects.create(
            title="Second dream",
            description="Second description",
            user=self.user
        )

        self.dream_with_likes = Dream.objects.create(
            title="Liked dream",
            description="With likes",
            user=self.user
        )
        self.dream_with_dislikes = Dream.objects.create(
            title="Disliked dream",
            description="With dislikes",
            user=self.user
        )

        DreamLike.objects.create(dream=self.dream_with_likes, owner=self.user)
        DreamDislike.objects.create(
            dream=self.dream_with_dislikes,
            owner=self.user
        )

    def test_queryset_with_title_search(self):
        response = self.client.get(
            DREAM_LIST_URL,
            {"title": "First"}
        )
        dreams = response.context["dreams"]
        self.assertEqual(len(dreams), 1)
        self.assertEqual("First dream", dreams[0].title)

    def test_queryset_with_likes_filter(self):
        response = self.client.get(
            DREAM_LIST_URL,
            {"filter": "likes"}
        )
        dreams = response.context["dreams"]
        self.assertEqual("Liked dream", dreams[0].title)

    def test_queryset_with_dislikes_filter(self):
        response = self.client.get(
            DREAM_LIST_URL,
            {"filter": "dislikes"}
        )
        dreams = response.context["dreams"]
        self.assertEqual("Disliked dream", dreams[0].title)

    def test_context_data(self):
        response = self.client.get(DREAM_LIST_URL)
        self.assertIn("dreams", response.context)
        self.assertIn("dream_search", response.context)
        self.assertIn("filter", response.context)

        self.assertEqual(
            "",
            response.context["dream_search"].initial["title"]
        )

    def test_detail_view(self):
        url = reverse(
            "dream:dream-detail",
            args=[str(self.user.pk), str(self.dream_with_likes.pk)]
        )
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "dream/dream_detail.html")
        self.assertEqual(
            str(True),
            response.cookies[str(self.dream_with_likes.pk)].value
        )

    def test_dream_create(self):
        url = reverse(
            "dream:dream-create",
            args=[str(self.user.pk)]
        )
        title = "New one"
        response = self.client.post(
            url,
            data={
                "title": title,
                "description": "New one descr..."
            }
        )

        self.assertEqual(302, response.status_code)
        self.assertTrue(Dream.objects.filter(title=title).exists())
        dream = Dream.objects.filter(title=title).first()
        self.assertEqual(self.user, dream.user)

    def test_dream_update_not_all_fields(self):
        dream_to_update = Dream.objects.create(
            user=self.user,
            title="old title",
            description="new description"
        )
        url = reverse(
            "dream:dream-update",
            args=[str(self.user.pk), str(dream_to_update.pk)]
        )
        title = "New one"
        response = self.client.post(
            url,
            data={
                "title": title,
            }
        )

        dream_to_update.refresh_from_db()
        self.assertEqual(302, response.status_code)
        self.assertEqual(title, dream_to_update.title)
        self.assertEqual("", dream_to_update.description)

    def test_dream_update_all_fields(self):
        url = reverse(
            "dream:dream-update",
            args=[str(self.user.pk), str(self.dream_with_likes.pk)]
        )
        title = "Title"
        description = "new one for tests"
        response = self.client.post(
            url,
            data={
                "title": title,
                "description": description,
            }
        )

        self.dream_with_likes.refresh_from_db()
        self.assertEqual(302, response.status_code)
        self.assertEqual(title, self.dream_with_likes.title)
        self.assertEqual(description, self.dream_with_likes.description)

    def test_dream_successful_delete(self):
        pk = self.dream_with_dislikes.pk
        url = reverse(
            "dream:dream-delete",
            args=[str(self.user.pk), str(pk)]
        )
        response = self.client.delete(url)

        self.assertEqual(302, response.status_code)
        self.assertFalse(Dream.objects.filter(pk=pk).exists())

    def test_dream_trying_to_delete_another_user(self):
        new_user = get_user_model().objects.create_user(
            username="new",
            password="pass",
            birth_date=datetime.date(2000, 2, 2)
        )
        self.client.force_login(new_user)
        delete_url = reverse(
            "dream:dream-delete",
            args=[
                str(self.user.id),
                str(self.dream_with_dislikes.id),
            ]
        )
        response = self.client.delete(delete_url)
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            "You do not have permission to delete this dream.",
            response.content.decode()
        )

    def test_dream_add_like_and_remove_it(self):
        dream_add_remove_like_url = reverse(
            "dream:dream-like",
            args=[
                str(self.user.id),
                str(self.dream_with_dislikes.id),
            ]
        )
        add_response = self.client.post(dream_add_remove_like_url)

        self.assertEqual(302, add_response.status_code)
        self.assertTrue(
            DreamLike.is_user_liked(self.user, self.dream_with_dislikes)
        )

        remove_response = self.client.post(dream_add_remove_like_url)

        self.assertEqual(302, remove_response.status_code)
        self.assertFalse(
            DreamLike.is_user_liked(self.user, self.dream_with_dislikes)
        )

    def test_dream_add_dislike_and_remove_it(self):
        dream_add_remove_dislike_url = reverse(
            "dream:dream-dislike",
            args=[
                str(self.user.id),
                str(self.dream_with_likes.id),
            ]
        )
        add_response = self.client.post(dream_add_remove_dislike_url)

        self.assertEqual(302, add_response.status_code)
        self.assertTrue(DreamDislike.is_user_disliked(
            self.user,
            self.dream_with_likes
        ))

        remove_response = self.client.post(dream_add_remove_dislike_url)

        self.assertEqual(302, remove_response.status_code)
        self.assertFalse(DreamDislike.is_user_disliked(
            self.user,
            self.dream_with_likes
        ))

    def test_dream_statistic(self):
        abuse = Emotion.objects.create(
            name="Abuse",
            description="Abuse..."
        )
        nice = Emotion.objects.create(
            name="Nice",
            description="Nice..."
        )

        horror = Symbol.objects.create(
            name="Horror",
            description="Horror...."
        )
        ghost = Symbol.objects.create(
            name="Ghost",
            description="Somrt",
        )
        self.dream_with_likes.symbols.add(horror, ghost)
        self.dream_with_likes.emotions.add(abuse, nice)
        self.dream_with_dislikes.symbols.add(horror, ghost)
        self.dream_with_dislikes.emotions.add(abuse, nice)

        url = reverse("dream:user-dream-statistic", args=[str(self.user.pk)])
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "dream/dream_statistic.html")

        dreams = self.user.dreams.all()
        top_of_emotions = EmotionDto.get_from_query_set(
            dreams.values("emotions__name", "emotions__description").annotate(
                total_count=Count("emotions__name")
            ).order_by("-total_count", "emotions__name")[:8]
        )

        top_of_symbols = SymbolDto.get_from_query_set(
            dreams.values("symbols__name", "symbols__description").annotate(
                total_count=Count("symbols__name")
            ).order_by("-total_count", "symbols__name")[:8]
        )
        self.assertEqual(self.user, response.context["current_user"])
        self.assertEqual(list(dreams), list(response.context["dreams"]))
        self.assertEqual(
            self.user.dreams.count(),
            response.context["count_dreams"]
        )
        self.assertEqual(
            top_of_emotions,
            response.context["top_of_emotions"]
        )
        self.assertEqual(
            top_of_symbols,
            response.context["top_of_symbols"]
        )
        self.assertEqual(
            [emotion.name for emotion in top_of_emotions],
            response.context["emotion_labels"]
        )
        self.assertEqual(
            [emotion.count for emotion in top_of_emotions],
            response.context["emotion_data"]
        )
        self.assertEqual(
            [symbol.name for symbol in top_of_symbols],
            response.context["symbol_labels"]
        )
        self.assertEqual(
            [symbol.count for symbol in top_of_symbols],
            response.context["symbol_data"]
        )
