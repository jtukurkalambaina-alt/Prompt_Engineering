"""A small multi-turn chat CLI with in-memory conversation history.

Run a local mock chat without an API key:
    python examples/multi_turn_chat.py --mock

Run with OpenAI when OPENAI_API_KEY is set:
    python examples/multi_turn_chat.py --model "$OPENAI_MODEL"
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Protocol


DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant. Use the conversation history to answer follow-up questions."
DEFAULT_MODEL = "gpt-4o-mini"


@dataclass(frozen=True)
class Message:
    """A single chat message."""

    role: str
    content: str

    def as_dict(self) -> dict[str, str]:
        """Return the wire format expected by chat-completion APIs."""
        return {"role": self.role, "content": self.content}


class ConversationMemory:
    """Stores the system prompt and the most recent user/assistant turns."""

    def __init__(self, system_prompt: str = DEFAULT_SYSTEM_PROMPT, max_turns: int = 8) -> None:
        if max_turns < 1:
            raise ValueError("max_turns must be at least 1")
        self.system_prompt = system_prompt
        self.max_turns = max_turns
        self._messages: list[Message] = []

    def add_user_message(self, content: str) -> None:
        """Append a user message to memory."""
        self._messages.append(Message(role="user", content=content))
        self._trim_history()

    def add_assistant_message(self, content: str) -> None:
        """Append an assistant message to memory."""
        self._messages.append(Message(role="assistant", content=content))
        self._trim_history()

    def build_messages(self) -> list[dict[str, str]]:
        """Build the full prompt payload, including system instructions and recent history."""
        messages = [Message(role="system", content=self.system_prompt), *self._messages]
        return [message.as_dict() for message in messages]

    def clear(self) -> None:
        """Forget all prior user and assistant messages."""
        self._messages.clear()

    def _trim_history(self) -> None:
        """Keep the last N turns, where each turn is a user/assistant pair."""
        max_messages = self.max_turns * 2
        if len(self._messages) > max_messages:
            self._messages = self._messages[-max_messages:]


class ChatClient(Protocol):
    """Interface for anything that can complete a chat conversation."""

    def complete(self, messages: list[dict[str, str]]) -> str:
        """Return the assistant response for a list of chat messages."""


class EchoChatClient:
    """Offline client for demos and tests.

    It proves history is being retained by mentioning the previous user turn in each reply.
    """

    def complete(self, messages: list[dict[str, str]]) -> str:
        user_messages = [message["content"] for message in messages if message["role"] == "user"]
        latest = user_messages[-1] if user_messages else ""
        previous = user_messages[-2] if len(user_messages) > 1 else None

        if previous:
            return f"You just said: '{latest}'. I also remember your previous turn: '{previous}'."
        return f"You just said: '{latest}'. I'll remember it for the next turn."


class OpenAIChatClient:
    """OpenAI-backed client that receives the full remembered message list each turn."""

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model

    def complete(self, messages: list[dict[str, str]]) -> str:
        from openai import OpenAI

        client = OpenAI()
        response = client.chat.completions.create(model=self.model, messages=messages)
        content = response.choices[0].message.content
        return content or ""


class MultiTurnChat:
    """Coordinates memory and model calls for a multi-turn chat."""

    def __init__(self, client: ChatClient, memory: ConversationMemory | None = None) -> None:
        self.client = client
        self.memory = memory or ConversationMemory()

    def respond(self, user_input: str) -> str:
        """Remember user input, call the model with history, and remember the answer."""
        cleaned_input = user_input.strip()
        if not cleaned_input:
            raise ValueError("user_input cannot be empty")

        self.memory.add_user_message(cleaned_input)
        assistant_response = self.client.complete(self.memory.build_messages())
        self.memory.add_assistant_message(assistant_response)
        return assistant_response


def interactive_chat(chat: MultiTurnChat) -> None:
    """Start an interactive terminal session."""
    print("Multi-turn chat started. Type 'exit' or 'quit' to stop, or '/clear' to reset memory.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Assistant: Goodbye!")
            break
        if user_input == "/clear":
            chat.memory.clear()
            print("Assistant: Memory cleared.")
            continue
        if not user_input:
            continue

        print(f"Assistant: {chat.respond(user_input)}")


def build_chat(use_mock: bool, model: str, max_turns: int) -> MultiTurnChat:
    """Construct a chat with either the offline mock client or the OpenAI client."""
    client: ChatClient = EchoChatClient() if use_mock else OpenAIChatClient(model=model)
    memory = ConversationMemory(max_turns=max_turns)
    return MultiTurnChat(client=client, memory=memory)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Multi-turn chat with conversation memory.")
    parser.add_argument("--mock", action="store_true", help="Run offline with a deterministic echo client.")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", DEFAULT_MODEL), help="OpenAI model name.")
    parser.add_argument("--max-turns", type=int, default=8, help="Number of recent user/assistant turns to keep.")
    return parser.parse_args()


def main() -> None:
    """Entrypoint for the CLI."""
    args = parse_args()
    chat = build_chat(use_mock=args.mock, model=args.model, max_turns=args.max_turns)
    interactive_chat(chat)


if __name__ == "__main__":
    main()
