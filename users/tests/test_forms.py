import datetime

from django.test import TestCase

from users.forms import CustomUserCreateForm


class FormTests(TestCase):
    def test_custom_user_create_form(self):
        create_form_data = {
            "username": "new_user",
            "email": "user@mail.co",
            "first_name": "First",
            "last_name": "Last",
            "birth_date": datetime.date(2001, 2, 12),
            "password1": "first_pass",
            "password2": "first_pass",
            "set_usable_password": True,
        }
        form = CustomUserCreateForm(data=create_form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(create_form_data, form.cleaned_data)
