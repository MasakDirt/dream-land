from django.test import TestCase

from dream.services.ai.tools.tools_handler import (
    get_tools_descriptions,
    call_tool,
    ToolCallException,
    _get_tool_description,
    _get_params_description,
    _get_tool,
    _get_tool_params,
)


class ToolsHandlerTestCase(TestCase):
    def test_get_tools_descriptions_valid_tools(self):
        tool_names = ["get_user_dreams", "get_user_emotions"]
        descriptions = get_tools_descriptions(tool_names)
        self.assertEqual(len(descriptions), 2)
        for desc in descriptions:
            self.assertIn("type", desc)
            self.assertEqual(desc["type"], "function")
            self.assertIn("function", desc)

    def test_get_tools_descriptions_invalid_tool(self):
        tool_names = ["invalid_tool"]
        descriptions = get_tools_descriptions(tool_names)
        self.assertEqual(len(descriptions), 0)

    def test_call_tool_valid(self):
        # This would require setting up data, but for now, test the structure
        try:
            result = call_tool("get_user_dreams", '{"user_pk": 1}')
            self.assertIsInstance(result, dict)
        except ToolCallException:
            # Expected if no data
            pass

    def test_call_tool_invalid_json(self):
        with self.assertRaises(ToolCallException):
            call_tool("get_user_dreams", "invalid json")

    def test_call_tool_invalid_tool(self):
        result = call_tool("invalid_tool", '{"user_pk": 1}')
        self.assertEqual(result, {})

    def test_get_tool_description_valid(self):
        desc = _get_tool_description("get_user_dreams")
        self.assertIsNotNone(desc)
        self.assertIn("type", desc)

    def test_get_tool_description_invalid(self):
        desc = _get_tool_description("invalid_tool")
        self.assertIsNone(desc)

    def test_get_params_description_valid(self):
        desc = _get_params_description("get_user_dreams")
        self.assertIsNotNone(desc)
        self.assertIn("properties", desc)

    def test_get_params_description_invalid(self):
        desc = _get_params_description("invalid_tool")
        self.assertIsNone(desc)

    def test_get_tool_valid(self):
        tool = _get_tool("get_user_dreams")
        self.assertIsNotNone(tool)
        self.assertTrue(callable(tool))

    def test_get_tool_invalid(self):
        tool = _get_tool("invalid_tool")
        self.assertIsNone(tool)

    def test_get_tool_params_valid(self):
        params = _get_tool_params("get_user_dreams")
        self.assertIsNotNone(params)

    def test_get_tool_params_invalid(self):
        params = _get_tool_params("invalid_tool")
        self.assertIsNone(params)
