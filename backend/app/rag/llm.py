import os
import time

from dotenv import load_dotenv
from google import genai


load_dotenv()


class LLM:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing "
                "from backend/.env"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-3.8-flash"

    def generate(self, prompt):

        max_retries = 3

        for attempt in range(max_retries):

            try:

                interaction = (
                    self.client.interactions.create(
                        model=self.model,
                        input=prompt
                    )
                )

                return interaction.output_text

            except Exception as error:

                print(
                    f"\nGemini request failed "
                    f"(attempt {attempt + 1}/{max_retries})"
                )

                print(error)

                if attempt < max_retries - 1:

                    wait_time = 2 ** attempt

                    print(
                        f"Retrying in "
                        f"{wait_time} seconds..."
                    )

                    time.sleep(wait_time)

                else:

                    raise RuntimeError(
                        "Gemini is currently unavailable. "
                        "Please try again later."
                    ) from error