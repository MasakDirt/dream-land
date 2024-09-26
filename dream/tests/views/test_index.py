import datetime

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.test import TestCase
from django.urls import reverse

from dto.dto import GraphicDto
from dream.models import Dream, Emotion, Commentary
from dream.views.index import get_dream_labels, get_emotion_labels


class PublicIndexTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="Main user",
            password="password",
            birth_date=datetime.date(2002, 8, 12)
        )
        self.abuse_dream = Dream.objects.create(
            title="Abuse",
            description="abuse descr..",
            user=self.user
        )
        self.killed_dream = Dream.objects.create(
            title="Killed",
            description="Killed descr..",
            user=self.user
        )
        self.comment = Commentary.objects.create(
            owner=self.user,
            dream=self.abuse_dream,
            content="Some content",
        )
        self.sadness = Emotion.objects.create(
            name="Sadness",
            description="Sadness"
        )
        self.abuse = Emotion.objects.create(
            name="Abuse",
            description="Abuse"
        )
        self.abuse_dream.emotions.add(self.abuse, self.sadness)
        self.killed_dream.emotions.add(self.abuse, self.sadness)

    def test_index_template(self):
        url = reverse("dream:index")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "dream/index.html")
        self.assertEqual(
            Dream.objects.count(),
            response.context["dreams_count"]
        )
        self.assertEqual(
            get_user_model().objects.count(),
            response.context["profiles_count"]
        )
        self.assertEqual(
            Commentary.objects.count(),
            response.context["commentary_count"]
        )
        month_today = datetime.date.today().month
        year_today = datetime.date.today().year
        profiles_month_count = get_user_model().objects.filter(
            date_joined__month=month_today,
            date_joined__year=year_today
        ).count()

        dreams_month_count = Dream.objects.filter(
            date_recorded__month=month_today,
            date_recorded__year=year_today
        ).count()

        commentary_month_count = Commentary.objects.filter(
            created_time__month=month_today,
            created_time__year=year_today
        ).count()
        self.assertEqual(
            profiles_month_count,
            response.context["profiles_month_count"]
        )
        self.assertEqual(
            dreams_month_count,
            response.context["dreams_month_count"]
        )
        self.assertEqual(
            commentary_month_count,
            response.context["commentary_month_count"]
        )

        dream_graphic = GraphicDto.get_from_query_set(
            Dream.objects.values(
                "date_recorded__month",
                "date_recorded__year"
            ).annotate(count=Count("title")).order_by(),
            get_dream_labels
        )
        top_emotions = GraphicDto.get_from_query_set(
            Dream.objects.values("emotions__name")
            .annotate(count=Count("title")).order_by("-count")[:10],
            get_emotion_labels
        )
        self.assertEqual(
            dream_graphic,
            response.context["dream_graphic"]
        )
        self.assertEqual(
            top_emotions,
            response.context["emotions_graphic"]
        )
