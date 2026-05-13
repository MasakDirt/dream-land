from django.test import TestCase

from dream.services.ai.prompts.chat_prompt import CHAT_SYSTEM_PROMPT, CHAT_TITLE_PROMPT
from dream.services.ai.prompts.summary_prompts import SUMMARY_PROMPT


class PromptsTestCase(TestCase):
    def test_chat_system_prompt_is_string(self):
        self.assertIsInstance(CHAT_SYSTEM_PROMPT, str)
        self.assertGreater(len(CHAT_SYSTEM_PROMPT), 0)

    def test_chat_title_prompt_is_string(self):
        self.assertIsInstance(CHAT_TITLE_PROMPT, str)
        self.assertGreater(len(CHAT_TITLE_PROMPT), 0)
        self.assertIn("{user_message}", CHAT_TITLE_PROMPT)

    def test_summary_prompt_is_string(self):
        self.assertIsInstance(SUMMARY_PROMPT, str)
        self.assertGreater(len(SUMMARY_PROMPT), 0)
