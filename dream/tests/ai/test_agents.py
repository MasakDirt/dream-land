from unittest.mock import Mock, patch

from django.test import TestCase
from openai.types.chat import ChatCompletionMessage

from dream.services.ai.agents.base_agent import BaseAgent
from dream.services.ai.agents.chat_agent import DreamsChatAgent
from dream.services.ai.agents.summary_agent import DreamsSummaryAgent


class AgentsTestCase(TestCase):
    def setUp(self):
        self.system_prompt = "Test system prompt"
        self.user_prompt = "Test user prompt"
        self.history = [{"role": "user", "content": "Hello"}]

    @patch('dream.services.ai.agents.base_agent.AzureOpenAI')
    def test_base_agent_init(self, mock_client):
        agent = BaseAgent(system_prompt=self.system_prompt)
        self.assertEqual(agent._BaseAgent__system_prompt, self.system_prompt)
        mock_client.assert_called_once()

    @patch('dream.services.ai.agents.base_agent.AzureOpenAI')
    def test_get_messages_no_history(self, mock_client):
        agent = BaseAgent(system_prompt=self.system_prompt)
        messages = agent.get_messages(self.user_prompt)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")

    @patch('dream.services.ai.agents.base_agent.AzureOpenAI')
    def test_get_messages_with_history(self, mock_client):
        agent = BaseAgent(system_prompt=self.system_prompt)
        messages = agent.get_messages(self.user_prompt, self.history)
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[1]["role"], "user")

    @patch('dream.services.ai.agents.base_agent.AzureOpenAI')
    def test_create_completion(self, mock_client):
        mock_completion = Mock()
        mock_message = Mock(spec=ChatCompletionMessage)
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_completion.choices = [mock_choice]
        mock_client.return_value.chat.completions.create.return_value = mock_completion

        agent = BaseAgent(system_prompt=self.system_prompt)
        messages = agent.get_messages(self.user_prompt)
        result = agent.create_completion(messages)
        self.assertEqual(result, mock_message)
        mock_client.return_value.chat.completions.create.assert_called_once()

    @patch('dream.services.ai.agents.base_agent.AzureOpenAI')
    @patch('dream.services.ai.agents.base_agent.call_tool')
    def test_run_tools(self, mock_call_tool, mock_client):
        mock_tool_call = Mock()
        mock_tool_call.function.name = "test_tool"
        mock_tool_call.function.arguments = '{"param": "value"}'
        mock_tool_call.id = "123"

        mock_message = Mock(spec=ChatCompletionMessage)
        mock_message.tool_calls = [mock_tool_call]

        mock_call_tool.return_value = {"result": "success"}

        agent = BaseAgent(system_prompt=self.system_prompt)
        results = agent.run_tools(mock_message)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["role"], "tool")
        mock_call_tool.assert_called_once_with(
            tool_name="test_tool",
            tool_arguments='{"param": "value"}'
        )

    @patch('dream.services.ai.agents.base_agent.AzureOpenAI')
    def test_run_agent_loop_success(self, mock_client):
        mock_completion = Mock()
        mock_message = Mock(spec=ChatCompletionMessage)
        mock_message.tool_calls = None
        mock_message.content = "Response"
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_completion.choices = [mock_choice]
        mock_client.return_value.chat.completions.create.return_value = mock_completion

        agent = BaseAgent(system_prompt=self.system_prompt)
        success, content = agent.run_agent_loop([], self.user_prompt)
        self.assertTrue(success)
        self.assertEqual(content, "Response")

    @patch('dream.services.ai.agents.base_agent.AzureOpenAI')
    def test_run_agent_loop_max_iterations(self, mock_client):
        mock_completion = Mock()
        mock_message = Mock(spec=ChatCompletionMessage)
        mock_message.tool_calls = [Mock()]  # Always has tool calls
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_completion.choices = [mock_choice]
        mock_client.return_value.chat.completions.create.return_value = mock_completion

        agent = BaseAgent(system_prompt=self.system_prompt, max_iterations=1)
        success, content = agent.run_agent_loop([], self.user_prompt)
        self.assertFalse(success)
        self.assertIsNone(content)

    @patch('dream.services.ai.agents.base_agent.AzureOpenAI')
    def test_chat_agent_init(self, mock_client):
        agent = DreamsChatAgent()
        self.assertIsInstance(agent, BaseAgent)

    @patch('dream.services.ai.agents.base_agent.AzureOpenAI')
    @patch('dream.services.ai.agents.base_agent.BaseAgent.run_agent_loop')
    def test_chat_agent_chat(self, mock_run_loop, mock_client):
        mock_run_loop.return_value = (True, "Chat response")
        agent = DreamsChatAgent()
        result = agent.chat(1, "Hello", [])
        self.assertEqual(result, "Chat response")
        mock_run_loop.assert_called_once()

    @patch('dream.services.ai.agents.base_agent.AzureOpenAI')
    @patch('dream.services.ai.agents.base_agent.BaseAgent.create_completion')
    def test_chat_agent_generate_title(self, mock_create_completion, mock_client):
        mock_message = Mock(spec=ChatCompletionMessage)
        mock_message.content = "Dream Title"
        mock_create_completion.return_value = mock_message

        agent = DreamsChatAgent()
        title = agent.generate_title("I had a dream about flying")
        self.assertEqual(title, "Dream Title")

    @patch('dream.services.ai.agents.base_agent.AzureOpenAI')
    @patch('dream.services.ai.agents.base_agent.BaseAgent.create_completion')
    def test_chat_agent_generate_title_exception(self, mock_create_completion, mock_client):
        mock_create_completion.side_effect = Exception("Error")

        agent = DreamsChatAgent()
        title = agent.generate_title("I had a dream about flying")
        self.assertEqual(title, "I had a dream about flying")

    @patch('dream.services.ai.agents.base_agent.AzureOpenAI')
    def test_summary_agent_init(self, mock_client):
        agent = DreamsSummaryAgent()
        self.assertIsInstance(agent, BaseAgent)

    @patch('dream.services.ai.agents.base_agent.AzureOpenAI')
    @patch('dream.services.ai.agents.base_agent.BaseAgent.run_agent_loop')
    def test_summary_agent_gen_statistic_summary(self, mock_run_loop, mock_client):
        mock_run_loop.return_value = (True, "Summary response")
        agent = DreamsSummaryAgent()
        result = agent.gen_statistic_summary(1)
        self.assertEqual(result, "Summary response")
        mock_run_loop.assert_called_once()
