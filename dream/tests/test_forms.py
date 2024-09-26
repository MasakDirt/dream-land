import datetime

from django.test import TestCase

from dream.forms import (
    DreamSearchForm,
    DreamFilterForm,
    DreamForm,
)


class FormTests(TestCase):
    def test_dream_search_form(self):
        search_form_data = {"title": "Search title for dream"}
        form = DreamSearchForm(data=search_form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(search_form_data, form.cleaned_data)

    def test_dream_filter_form(self):
        filter_form_data = {"filter": "likes"}
        form = DreamFilterForm(data=filter_form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(filter_form_data, form.cleaned_data)

        filter_form_data = {"filter": "likessss"}
        form = DreamFilterForm(data=filter_form_data)

        self.assertFalse(form.is_valid())

    def test_dream_form(self):
        dream_form_data = {
            "title": "Title dream",
            "description": "description dream",
            "emotions": [],
            "symbols": [],
        }
        form = DreamForm(data=dream_form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(dream_form_data["title"], form.cleaned_data["title"])
        self.assertEqual(
            dream_form_data["description"],
            form.cleaned_data["description"]
        )
        self.assertEqual(
            dream_form_data["emotions"],
            list(form.cleaned_data["emotions"])
        )
        self.assertEqual(
            dream_form_data["symbols"],
            list(form.cleaned_data["symbols"])
        )
