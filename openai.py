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

    def _add_preprompt(
        self, messages: list[ChatCompletionMessageParam]
    ) -> list[ChatCompletionMessageParam]:
        messages.insert(
            0,
            {
                "content": self.pre_prompt or "",
                "role": "system",
                "name": "BlitzUI",
            },
        )
        return messages

    def refresh_client(self, api_key: str) -> None:
        self._api_key = api_key
        self.client = self._get_client(api_key=api_key)

    async def stream(
        self, messages: list[ChatCompletionMessageParam]
    ) -> AsyncStream[ChatCompletion]:
        if self.pre_prompt:
            messages = self._add_preprompt(messages)
        if self.client is None:
            # TODO: handle this error
            raise Exception
        return cast(
            AsyncStream[ChatCompletion],
            await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
            ),
        )

    async def list_models(self) -> Any:
        if self.client is None:
            # TODO: handle this error
            raise Exception
        return await self.client.models.list()
