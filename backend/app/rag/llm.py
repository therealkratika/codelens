import os
import time
from collections.abc import Callable

import httpx
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from google.genai import types


load_dotenv()


class LLM:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing "
                "from backend/.env"
            )

        print("Initializing Gemini...")

        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=60_000,
                retry_options=types.HttpRetryOptions(
                    attempts=1
                )
            )
        )

        self.model = "gemini-3.8-flash"

        print("Gemini initialized!")

    def generate(
        self,
        prompt,
        on_text: Callable[[str], None] | None = None
    ):

        max_attempts = 3
        retryable_status_codes = {
            408,
            429,
            500,
            502,
            503,
            504
        }

        for attempt in range(max_attempts):
            output_parts = []

            try:
                print(
                    f"Calling Gemini "
                    f"(attempt {attempt + 1}/{max_attempts}); "
                    "waiting for streamed response...",
                    flush=True
                )

                response_stream = (
                    self.client.models.generate_content_stream(
                        model=self.model,
                        contents=prompt
                    )
                )

                for response in response_stream:
                    text = response.text

                    if not text:
                        continue

                    output_parts.append(text)

                    if on_text is not None:
                        on_text(text)

                answer = "".join(output_parts)

                if not answer:
                    raise RuntimeError(
                        "Gemini completed but returned no text."
                    )

                print(
                    "\nGemini response received.",
                    flush=True
                )
                return answer

            except httpx.TimeoutException as error:
                if output_parts:
                    partial_answer = "".join(output_parts)

                    print(
                        "\nGemini stream timed out, "
                        "returning partial response.",
                        flush=True
                    )

                    return partial_answer

                if attempt + 1 < max_attempts:
                    wait_seconds = 2 ** attempt

                    print(
                        "Gemini stream timed out before producing text; "
                        f"retrying in {wait_seconds} seconds.",
                        flush=True
                    )
                    time.sleep(wait_seconds)
                    continue

                print(
                    f"\nGemini request timed out: {error}",
                    flush=True
                )
                raise RuntimeError(
                    "Gemini timed out before returning any text after "
                    f"{max_attempts} attempts. Please try again later."
                ) from error

            except errors.APIError as error:
                can_retry = (
                    error.code in retryable_status_codes
                    and not output_parts
                    and attempt + 1 < max_attempts
                )

                if can_retry:
                    wait_seconds = 2 ** attempt

                    print(
                        f"Gemini returned HTTP {error.code}; "
                        f"retrying in {wait_seconds} seconds.",
                        flush=True
                    )
                    time.sleep(wait_seconds)
                    continue

                print(
                    f"\nGemini request failed: {error}",
                    flush=True
                )

                if output_parts:
                    partial_answer = "".join(output_parts)

                    print(
                        "\nGemini stream interrupted, "
                        "returning partial response.",
                        flush=True
                    )

                    return partial_answer

                if error.code in retryable_status_codes:
                    raise RuntimeError(
                        f"Gemini remained unavailable after "
                        f"{attempt + 1} attempt(s) "
                        f"(HTTP {error.code}). Please try again later."
                    ) from error

                raise RuntimeError(
                    "Gemini rejected the request. Check the API "
                    "key, model name, and request configuration."
                ) from error

            except Exception as error:
                print(
                    f"\nGemini request failed: {error}",
                    flush=True
                )

                raise RuntimeError(
                    "Gemini could not complete the response. "
                    "Check the model name, API key, and network "
                    "connection, then try again."
                ) from error