# AI Automation Agent

A production-style AI agent built with LangGraph and Django REST Framework. Send plain-English requests to a REST API and the agent automatically selects the right tool, executes it, and returns a natural language response — with full conversation memory across turns.

---

## What it does

- Answers questions by intelligently routing to the correct tool
- Remembers conversation history within a session via `session_id`
- Exposes a clean REST API endpoint so it can be called from any frontend or service

---

## Tech stack

- **Python** — core language
- **LangGraph** — agent loop and state management
- **LangChain** — LLM integration and tool calling
- **OpenAI GPT-4o-mini** — language model
- **Django + Django REST Framework** — REST API layer
- **Open-Meteo API** — live weather data (no API key required)
- **Pydantic** — tool input validation
- **uv** — dependency and environment management

---

## Project structure

```
ai_agent/
├── agent/
│   ├── __init__.py
│   ├── graph.py        # LangGraph agent loop and routing logic
│   ├── state.py        # shared AgentState definition
│   └── tools.py        # tool definitions with Pydantic validation
├── api/
│   ├── views.py        # Django REST endpoint
│   └── urls.py         # API routing
├── core/
│   ├── settings.py
│   └── urls.py
├── main.py             # interactive CLI (optional)
├── .env                # API keys (not committed)
└── pyproject.toml
```

---

## How the agent works

The agent runs a loop managed by LangGraph:

1. User sends a message to the API
2. The LLM reads the message and decides which tool to use based on tool descriptions
3. LangGraph routes to the selected tool and executes it
4. The tool result is fed back to the LLM
5. The LLM generates a natural language response
6. Steps 2-5 repeat until the LLM has enough to answer

If no tool matches, the LLM answers from its own knowledge.

---

## Available tools

| Tool | Description |
|---|---|
| `get_weather` | Live weather for any city via Open-Meteo |
| `calculate` | Evaluates math expressions |
| `search_knowledge_base` | Searches internal KB for Python, Django, LangGraph |

---

## Setup

### Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) installed
- OpenAI API key

### Install

```bash
git clone https://github.com/yourusername/ai-agent.git
cd ai-agent
uv sync
```

### Configure environment

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_key_here
```

### Run the server

```bash
uv run python manage.py runserver
```

---

## API usage

### Endpoint

```
POST /api/chat/
```

### Request body

```json
{
  "message": "What is the weather in Wichita, KS?",
  "session_id": "user_123"
}
```

- `message` — required, the user's plain-English input
- `session_id` — optional, ties messages into a conversation session for memory. Defaults to `"default"`

### Response

```json
{
  "message": "The current weather in Wichita is 45.5°F with a humidity of 34% and wind speed of 12.9 mph.",
  "session_id": "user_123"
}
```

---

## Example requests

**Weather:**
```bash
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather in New York?", "session_id": "demo"}'
```

**Math:**
```bash
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 347 multiplied by 12?", "session_id": "demo"}'
```

**Knowledge base:**
```bash
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about Django", "session_id": "demo"}'
```

**Memory across turns:**
```bash
# First message
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather in Kansas?", "session_id": "demo"}'

# Second message — agent remembers the first
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What did I just ask you?", "session_id": "demo"}'
```

---

## Running the CLI

An interactive command-line interface is also available:

```bash
uv run main.py
```

Type `quit` to exit.

---

## Extending the agent

To add a new tool, define it in `agent/tools.py` and add it to the `tools` list in `agent/graph.py`:

```python
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class MyToolInput(BaseModel):
    query: str = Field(description="Description of what this input does")

@tool(args_schema=MyToolInput)
def my_tool(query: str) -> str:
    """Clear description — the LLM reads this to decide when to use the tool."""
    return "tool result"
```

The agent will automatically route to it when appropriate — no other changes needed.

---

## Author

Jeremiah Emrich — [github.com/jeremiahemrich](https://github.com/jemrich18)
