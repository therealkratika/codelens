import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


class LLM:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing from backend/.env"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-3.8-flash"

    def generate(self, prompt):

        interaction = self.client.interactions.create(
            model=self.model,
            input=prompt
        )

        return interaction.output_text