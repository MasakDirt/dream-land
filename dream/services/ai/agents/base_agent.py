import json
import logging
from typing import Any

from django.conf import settings
from openai import AzureOpenAI
from openai.types.chat import ChatCompletionMessage

from dream.services.ai.tools.tools_handler import call_tool, ToolCallException

logger = logging.getLogger("dreams")


class BaseAgent:
    def __init__(
        self,
        system_prompt: str,
        model: str | None = None,
        max_iterations: int = 10,
        api_version: str = "2024-02-01",
    ):
        self.__client = AzureOpenAI(
            api_key=settings.SYSTEM_AI_PROVIDER_API_KEY,
            azure_endpoint=settings.SYSTEM_AI_PROVIDER_BASE_URL,
            api_version=api_version,
        )
        self.__model = model or settings.SYSTEM_AI_PROVIDER_MODEL
        self._max_iterations = max_iterations
        self.__system_prompt = system_prompt

    def run_tools(self, message: ChatCompletionMessage) -> list:
        results = []
        for tool_call in message.tool_calls:
            try:
                tool_result = call_tool(
                    tool_name=tool_call.function.name,
                    tool_arguments=tool_call.function.arguments
                )
            except ToolCallException as e:
                logger.error(f"Failed to call tool: {e}")
                tool_result = {"error": f"Tool '{tool_call.function.name}' raised an error, error: {e}"}

            try:
                encoded_result = json.dumps(tool_result)
            except TypeError as e:
                logger.error(f"Failed to encode tool result: {e}")
                encoded_result = tool_result

            results.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": encoded_result,
                }
            )

        return results

    def get_messages(self, user_prompt: str, history_before: list | None = None) -> list[dict[str, Any]]:
        messages = [
            {"role": "system", "content": self.__system_prompt},
        ]

        if history_before:
            messages.extend(history_before)

        messages.append(
            {
                "role": "user",
                "content": user_prompt,
            }
        )

        return messages

    def create_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list | None = None
    ) -> ChatCompletionMessage:
        completions_kwargs = {
            "messages": messages,
            "model": self.__model,
        }
        if tools:
            completions_kwargs["tools"] = tools

        return self.__client.chat.completions.create(**completions_kwargs).choices[0].message

    def run_agent_loop(
        self, tools: list[dict[str, Any]],
        user_prompt: str,
        history: list[dict[str, Any]] | None = None
    ) -> tuple[bool, str | None]:
        messages = self.get_messages(user_prompt=user_prompt, history_before=history)
        max_exceptions = 5
        exceptions_count = 0

        for iteration in range(1, self._max_iterations):
            try:
                logger.info(f"Agent loop, iteration {iteration}/{self._max_iterations}")

                message = self.create_completion(messages=messages, tools=tools)
                messages.append(message)

                if message.tool_calls:
                    tool_messages = self.run_tools(message)
                    messages.extend(tool_messages)
                    continue

                return True, message.content

            except Exception as e:
                logger.error(f"Failed to chat, iteration: {iteration}/{self._max_iterations}")
                logger.error(e)

                exceptions_count += 1
                if exceptions_count >= max_exceptions:
                    return True, f"Failed to generate ai response, max exceptions reached: {str(e)[:200]}"

                continue

        return False, None
