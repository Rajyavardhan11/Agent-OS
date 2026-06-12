# Agent OS

Agent OS is a production-oriented multi-agent AI workspace. A user submits a complex task, the router selects specialized agents, and the system coordinates planning, research, coding, writing, critique, shared memory, and live progress streaming.

The backend uses FastAPI, LangGraph, ChromaDB, Ollama, Tavily, and sentence-transformers. The frontend is a dark Next.js dashboard with a live agent timeline, router decision visualization, final markdown output, and a memory panel for previously learned results.

## Architecture

```text
User Task
   |
   v
FastAPI / SSE
   |
   v
LangGraph StateGraph
   |
   +--> Memory Manager --> Router
                         |
                         v
             execution_order groups
                         |
             +-----------+-----------+
             |                       |
          Planner             Parallel Agents
             |                 Researcher + Coder
             v                       |
           Writer <------------------+
             |
             v
           Critic
             |
             v
Final Output + Long-Term Chroma Memory
```

## Tech Stack

| Layer | Tools |
| --- | --- |
| Backend API | Python 3.11, FastAPI, uvicorn, SSE-Starlette |
| Orchestration | LangGraph 0.2+, StateGraph, router-selected parallel groups |
| Memory | ChromaDB 0.5+, sentence-transformers all-MiniLM-L6-v2 |
| LLM | Ollama llama3.2 with mistral fallback |
| Search | Tavily Python SDK with offline fallback |
| Frontend | Next.js app router, TypeScript, Tailwind CSS, Framer Motion |
| Testing | pytest, pytest-asyncio |

## Prerequisites

Install Ollama and pull the default model:

```bash
ollama pull llama3.2
```

Optional fallback model:

```bash
ollama pull mistral
```

## Setup

Backend:

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Docker

From the project root:

```bash
docker-compose up --build
```

The backend runs on `http://localhost:8000` and the frontend runs on `http://localhost:3000`. ChromaDB data persists in the `chroma_db` Docker volume.

## Demo Tasks

- `Research top AI frameworks and compare them`
  Expected output: a sourced comparison brief with a critic score.
- `Build a FastAPI CRUD app with SQLite`
  Expected output: implementation plan, generated code, and review notes.
- `Write a blog post about the future of AI agents`
  Expected output: polished markdown article with improvements from the critic.

## Shared Memory

Agent OS uses two Chroma collections. `task_memory` stores short-lived working context from planner, researcher, coder, and writer agents. `long_term_memory` stores final critic-approved outputs with task metadata and quality scores, so future router and memory manager runs can retrieve relevant context.

Use `GET /api/memory` to inspect recent long-term memories and `DELETE /api/memory` to reset both collections.

## Adding A New Agent

1. Create `backend/agents/my_agent.py` and subclass `BaseAgent`.
2. Implement `async run(self, state) -> dict` and return only state updates.
3. Store useful work in `task_memory` or `long_term_memory`.
4. Register the agent in `AGENTS` inside `backend/graph/agent_graph.py`.
5. Teach `RouterAgent` to include the new agent in `agents_needed` and `execution_order`.
6. Add a frontend icon or display name in `frontend/components/AgentCard.tsx`.

## API

- `POST /api/task` with `{"task":"..."}` runs a task synchronously.
- `GET /api/task/{task_id}/stream?task=...` streams live agent events over SSE.
- `GET /api/tasks/history` returns the last 10 long-term task outputs.
- `GET /api/memory` returns recent memory entries.
- `DELETE /api/memory` clears all memory.

## Notes

If Ollama is not running, the backend logs a warning and the agents return clear fallback messages rather than crashing. If `TAVILY_API_KEY` is not set, research returns an explicit search-unavailable result.
