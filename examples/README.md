# Multi-turn Chat with Conversation History

This example implements a terminal chat loop that remembers previous user and assistant messages. The remembered messages are sent with each new request so the assistant can answer follow-up questions in context.

## Run locally without an API key

```bash
python examples/multi_turn_chat.py --mock
```

The mock client is deterministic and echoes the latest and previous user turns, which makes it easy to verify that memory is working.

## Run with OpenAI

Set your API key, optionally set a model, and run the script without `--mock`:

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="gpt-4o-mini"
python examples/multi_turn_chat.py
```

## Useful commands inside the chat

- `/clear` resets conversation memory.
- `exit` or `quit` ends the session.

## How memory works

`ConversationMemory` stores a system prompt plus the most recent user/assistant turns. `MultiTurnChat.respond()` adds the new user message, calls the chat client with the complete remembered context, then stores the assistant response for future turns.
