import logging

from dream.services.ai.agents.base_agent import BaseAgent
from dream.services.ai.prompts.chat_prompt import CHAT_SYSTEM_PROMPT, CHAT_TITLE_PROMPT
from dream.services.ai.tools.tools_handler import get_tools_descriptions

logger = logging.getLogger("dreams")


class DreamsChatAgent(BaseAgent):
    def __init__(
        self,
        model: str | None = None,
        max_iterations: int = 10,
        api_version: str = "2024-02-01",
    ):
        super().__init__(
            system_prompt=CHAT_SYSTEM_PROMPT,
            model=model,
            max_iterations=max_iterations,
            api_version=api_version,
        )

    def chat(self, user_pk: str | int, user_prompt: str, history: list[dict[str, str]]) -> str:
        """Chat with agent about dreams"""
        tools = get_tools_descriptions(
            [
                "get_user_dreams",
                "get_user_emotions",
                "get_user_symbols",
                "get_user_subscribers"
            ]
        )
        user_prompt = user_prompt + f"\n\n(User PK: {user_pk})"
        success, content = self.run_agent_loop(
            tools=tools,
            user_prompt=user_prompt,
            history=history,
        )
        if success:
            return content

        logger.info("Max iterations reached while chatting.")
        return "Failed to generate chat response, max iterations reached."

    def generate_title(self, user_message: str) -> str:
        """Ask AI for a short thread title based on the first user message."""
        default_title = user_message[:60]
        try:
            title = self.create_completion(
                messages=[{
                    "role": "user",
                    "content": CHAT_TITLE_PROMPT.format(user_message=user_message),
                }],
            ).content

            if not title:
                return default_title

            return title
        except Exception:
            return default_title
