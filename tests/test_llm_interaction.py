import unittest
from unittest.mock import patch, MagicMock
from vocalai.llm_interaction import LLMInteraction


class MockConfig:
    def __init__(self, instructions, llm_url, llm_model):
        self.instructions = instructions
        self.llm_url = llm_url
        self.llm_model = llm_model

class TestLLMInteraction(unittest.TestCase):
    def setUp(self):
        self.config = MockConfig(
            instructions="Please respond to: ",
            llm_url="http://fake-url.com/api",
            llm_model="generic-large-model"
        )
        self.llm_interaction = LLMInteraction(self.config)

    @patch('torch.cuda.is_available')
    def test_device_selection(self, mock_cuda_avail):
        mock_cuda_avail.return_value = True
        llm_interaction = LLMInteraction(self.config)
        self.assertEqual(llm_interaction.device, "cuda")

        mock_cuda_avail.return_value = False
        llm_interaction = LLMInteraction(self.config)
        self.assertEqual(llm_interaction.device, "cpu")

    @patch('requests.post')
    def test_query_llm_successful(self, mock_post):
        # Set up the mock to return a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"response":"Hello, world!"}\n{"response":" How are you?"}'
        mock_post.return_value = mock_response

        prompt = "Hello LLM"
        expected_response = "Hello, world! How are you?"
        result = self.llm_interaction.query_llm(prompt)
        self.assertEqual(result, expected_response)
        mock_post.assert_called_once_with(self.config.llm_url, json={'model': self.config.llm_model, 'prompt': self.config.instructions + prompt})

    @patch('requests.post')
    def test_query_llm_failure(self, mock_post):
        # Set up the mock to return a failed response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = 'Bad request'
        mock_post.return_value = mock_response

        prompt = "Hello LLM"
        with self.assertRaises(Exception) as context:
            self.llm_interaction.query_llm(prompt)

        self.assertIn('LLM query failed: 400 Bad request', str(context.exception))
