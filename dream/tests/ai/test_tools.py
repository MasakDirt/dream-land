import datetime

from django.test import TestCase

from dream.models import Dream, Emotion, Symbol
from dream.services.ai.tools.chat_tools import (
    get_user_dreams,
    UserDreamsParams,
    get_user_emotions,
    UserEmotionsFiltersParams,
    get_user_symbols,
    UserSymbolsFiltersParams,
    get_user_subscribers,
    UserSubscribersParams,
)
from dream.services.ai.tools.summary_tools import get_user_statistic, UserStatisticParams
from users.models import User


class ToolsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="password123",
            birth_date=datetime.date(1990, 1, 1)
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="password123",
            birth_date=datetime.date(1990, 1, 1)
        )
        self.emotion_happy = Emotion.objects.create(name="Happy", description="Feeling of joy")
        self.emotion_sad = Emotion.objects.create(name="Sad", description="Feeling of sorrow")
        self.symbol_water = Symbol.objects.create(name="Water", description="Symbol of fluidity")
        self.symbol_fire = Symbol.objects.create(name="Fire", description="Symbol of passion")

        self.dream1 = Dream.objects.create(
            title="Dream 1",
            description="A happy dream with water",
            user=self.user
        )
        Dream.objects.filter(pk=self.dream1.pk).update(date_recorded=datetime.date(2023, 1, 1))
        self.dream1.refresh_from_db()
        self.dream1.emotions.add(self.emotion_happy)
        self.dream1.symbols.add(self.symbol_water)

        self.dream2 = Dream.objects.create(
            title="Dream 2",
            description="A sad dream with fire",
            user=self.user
        )
        Dream.objects.filter(pk=self.dream2.pk).update(date_recorded=datetime.date(2023, 2, 1))
        self.dream2.refresh_from_db()
        self.dream2.emotions.add(self.emotion_sad)
        self.dream2.symbols.add(self.symbol_fire)

    def test_get_user_dreams_no_filters(self):
        params = UserDreamsParams(user_pk=self.user.pk)
        result = get_user_dreams(params)
        self.assertIn("dreams", result)
        self.assertEqual(len(result["dreams"]), 2)
        self.assertEqual(result["dreams"][0]["title"], "Dream 1")
        self.assertEqual(result["dreams"][1]["title"], "Dream 2")

    def test_get_user_dreams_with_emotion_filter(self):
        params = UserDreamsParams(
            user_pk=self.user.pk,
            emotions=[{"name": "Happy"}]
        )
        result = get_user_dreams(params)
        self.assertEqual(len(result["dreams"]), 1)
        self.assertEqual(result["dreams"][0]["title"], "Dream 1")

    def test_get_user_dreams_with_symbol_filter(self):
        params = UserDreamsParams(
            user_pk=self.user.pk,
            symbols=[{"name": "Water"}]
        )
        result = get_user_dreams(params)
        self.assertEqual(len(result["dreams"]), 1)
        self.assertEqual(result["dreams"][0]["title"], "Dream 1")

    def test_get_user_dreams_with_date_filter(self):
        params = UserDreamsParams(
            user_pk=self.user.pk,
            date_recorded_gte=datetime.date(2023, 1, 15)
        )
        result = get_user_dreams(params)
        self.assertEqual(len(result["dreams"]), 1)
        self.assertEqual(result["dreams"][0]["title"], "Dream 2")

    def test_get_user_emotions(self):
        params = UserEmotionsFiltersParams(user_pk=self.user.pk)
        result = get_user_emotions(params)
        self.assertIn("emotions", result)
        self.assertEqual(len(result["emotions"]), 2)
        emotion_names = [e["name"] for e in result["emotions"]]
        self.assertIn("Happy", emotion_names)
        self.assertIn("Sad", emotion_names)

    def test_get_user_symbols(self):
        params = UserSymbolsFiltersParams(user_pk=self.user.pk)
        result = get_user_symbols(params)
        self.assertIn("symbols", result)
        self.assertEqual(len(result["symbols"]), 2)
        symbol_names = [s["name"] for s in result["symbols"]]
        self.assertIn("Water", symbol_names)
        self.assertIn("Fire", symbol_names)

    def test_get_user_subscribers(self):
        # Create a follow relationship
        from users.models import Follow
        Follow.objects.create(follower=self.other_user, followed=self.user)

        params = UserSubscribersParams(user_pk=self.user.pk)
        result = get_user_subscribers(params)
        self.assertIn("subscribers", result)
        self.assertEqual(len(result["subscribers"]), 1)
        self.assertEqual(result["subscribers"][0]["follower__username"], "otheruser")

    def test_get_user_statistic(self):
        params = UserStatisticParams(user_pk=self.user.pk)
        result = get_user_statistic(params)
        self.assertIn("current_user", result)
        self.assertEqual(result["current_user"]["username"], "testuser")
        self.assertEqual(result["count_dreams"], 2)
        self.assertIn("top_of_emotions", result)
        self.assertIn("top_of_symbols", result)
