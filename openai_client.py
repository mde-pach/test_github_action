from openai import OpenAI
import os


class GPTClient:
    def __init__(
        self, api_key: str, model: str = "gpt-3.5-turbo", pre_prompt: str | None = None
    ) -> None:
        self.model = model
        self._api_key = api_key
        self.pre_prompt = pre_prompt
        self.client = self._get_client(api_key=api_key) if api_key else None

    @staticmethod
    def _get_client(api_key: str) -> OpenAI:
        return OpenAI(api_key=api_key)

    def _add_preprompt(self, messages: list) -> list:
        messages.insert(
            0,
            {
                "content": self.pre_prompt or "",
                "role": "system",
            },
        )
        return messages

    def refresh_client(self, api_key: str) -> None:
        self._api_key = api_key
        self.client = self._get_client(api_key=api_key)

    def ask(self, messages: list) -> None:
        if self.pre_prompt:
            messages = self._add_preprompt(messages)
        if self.client is None:
            # TODO: handle this error
            raise Exception
        return self.client.chat.completions.create(model=self.model, messages=messages)