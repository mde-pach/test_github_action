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


gpt = GPTClient(
    api_key=os.environ.get("OPENAI_API_KEY"),
    pre_prompt=(
        "You are a github application designed to help code maintainability. "
        "You will receive a git diff of a python code and the docstring of the function. "
        'You must answer with a json only formatted as {"docstring": '
        "}"
        "If the diff doesn't alter the function docstring, you should return null as the docstring. "
        "If the diff alters the function docstring, you should return the new docstring as the docstring. "
        "Consider only as an alteration if the diff is about something already present in the docstring. "
    ),
)


print(
    gpt.ask(
        [
            {
                "content": """

""",
                "role": "user",
            }
        ]
    )
    .choices[0]
    .message.content
)


def print_toto():
    print("toto")