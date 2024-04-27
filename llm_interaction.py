import json
import logging
import requests
import torch
from io import StringIO

class LLMInteraction:
    def __init__(self, config):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.instructions = config.instructions
        self.llm_url = config.llm_url
        self.llm_model = config.llm_model
        self.logger = logging.getLogger(__name__)

    def query_llm(self, prompt):
        parameters = {
            "model": self.llm_model,
            "prompt": self.instructions + prompt
        }

        response = requests.post(self.llm_url, json=parameters)

        if response.status_code == 200:
            response_text = response.text.strip()
            json_strings = response_text.split("\n")
            cummulative_response = StringIO()

            for json_str in json_strings:
                try:
                    json_obj = json.loads(json_str)
                    cummulative_response.write(json_obj["response"])
                except requests.exceptions.JSONDecodeError:
                    print("Error decoding JSON:", json_str)

            answer = cummulative_response.getvalue()
            cummulative_response.close()
            return answer
        else:
            raise Exception(f"LLM query failed: {response.status_code} {response.text}")

