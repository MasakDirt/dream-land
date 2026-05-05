import json
import logging
from typing import Callable, Any

from pydantic import BaseModel

from dream.services.ai.tools.summary_tools import get_user_statistic, UserStatisticParams
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

logger = logging.getLogger("dreams")

__TOOLS_HANDLER: dict[str, Callable] = {
    get_user_statistic.__name__: get_user_statistic,
    get_user_dreams.__name__: get_user_dreams,
    get_user_emotions.__name__: get_user_emotions,
    get_user_symbols.__name__: get_user_symbols,
    get_user_subscribers.__name__: get_user_subscribers,
}

__TOOLS_PARAMS_HANDLER: dict[str, type[BaseModel]] = {
    get_user_statistic.__name__: UserStatisticParams,
    get_user_dreams.__name__: UserDreamsParams,
    get_user_emotions.__name__: UserEmotionsFiltersParams,
    get_user_symbols.__name__: UserSymbolsFiltersParams,
    get_user_subscribers.__name__: UserSubscribersParams,
}


class ToolCallException(Exception):
    """Specific exception for tool call"""

    def __init__(self, message: str = ""):
        super().__init__(message)


def get_tools_descriptions(tool_names: list[str]) -> list[dict[str, Any]]:
    """Get tools descriptions"""
    try:
        tools_description = []
        for tool_name in tool_names:
            tool_description = _get_tool_description(tool_name)
            if not tool_description:
                continue

            tools_description.append(tool_description)

        return tools_description
    except Exception as e:
        logger.error(f"Tools description generation failed:\n{e}", exc_info=True)
        raise ToolCallException(f"Failed to generate tools description, exception: {str(e)[:200]}")


def call_tool(tool_name: str, tool_arguments: str) -> dict[str, Any]:
    """Call tool with given arguments"""
    try:
        tool_arguments = json.loads(tool_arguments)
        params = _get_tool_params(tool_name)
        if params is None:
            return {}

        params = params(**tool_arguments)
        tool = _get_tool(tool_name)
        if tool is None:
            return {}

        return tool(params)
    except Exception as e:
        logger.error(f"Tools calling failed:\n{e}", exc_info=True)
        raise ToolCallException(f"Failed to call tool: {tool_name}, exception: {str(e)[:200]}")


def _get_tool_description(tool_name: str) -> dict[str, Any] | None:
    tool = _get_tool(tool_name)
    if tool is None:
        return None

    return {
        "type": "function",
        "function": {
            "name": tool_name,
            "description": tool.__doc__,
            "parameters": _get_params_description(tool_name)
        }
    }


def _get_params_description(tool_name: str) -> dict[str, Any] | None:
    params = _get_tool_params(tool_name)
    if params is None:
        return None

    return params.model_json_schema()


def _get_tool(tool_name: str) -> Callable | None:
    return __TOOLS_HANDLER.get(tool_name, None)


def _get_tool_params(tool_name: str) -> type[BaseModel] | None:
    return __TOOLS_PARAMS_HANDLER.get(tool_name, None)
