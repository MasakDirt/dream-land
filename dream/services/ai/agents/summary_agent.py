import logging

from dream.services.ai.agents.base_agent import BaseAgent
from dream.services.ai.prompts.summary_prompts import SUMMARY_PROMPT
from dream.services.ai.tools.tools_handler import get_tools_descriptions

logger = logging.getLogger("dreams")


class DreamsSummaryAgent(BaseAgent):
    def __init__(
        self,
        model: str | None = None,
        max_iterations: int = 10,
        api_version: str = "2024-02-01",
    ):
        super().__init__(
            system_prompt=SUMMARY_PROMPT,
            model=model,
            max_iterations=max_iterations,
            api_version=api_version,
        )

    def gen_statistic_summary(self, user_pk: str | int) -> str:
        """Generates summary statistics for user dreams!"""
        tools = get_tools_descriptions(["get_user_statistic"])

        success, content = self.run_agent_loop(
            tools=tools,
            user_prompt=f"Generate summary for user: {user_pk}",
        )
        if success:
            return content

        logger.info("Max iterations reached while generating summary statistics for user dreams.")
        return "Failed to generate summary statistics for user dreams, max iterations reached."
