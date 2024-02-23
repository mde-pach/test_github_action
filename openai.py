from openai import AsyncOpenAI


class GPTClient:
    def __init__(
        self, api_key: str, model: str = "gpt-3.5-turbo", pre_prompt: str | None = None
    ) -> None:
        self.model = model
        self._api_key = api_key
        self.pre_prompt = pre_prompt
        self.client = self._get_client(api_key=api_key) if api_key else None

    @staticmethod
    def _get_client(api_key: str) -> AsyncOpenAI:
        return AsyncOpenAI(api_key=api_key)

    def refresh_client(self, api_key: str) -> None:
        self._api_key = api_key
        self.client = self._get_client(api_key=api_key)

    def ask(self, prompt: str) -> str:
        return self.client.GPTClient.ask(
            prompt=prompt, model=self.model, pre_prompt=self.pre_prompt
        )