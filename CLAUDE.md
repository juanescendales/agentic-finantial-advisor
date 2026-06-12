# CLAUDE.md — Agentic Financial Advisor

## Project Purpose

Educational project that simulates a **news-driven financial advising system** built as an observable and evaluable multi-agent pipeline. The primary goal is not production readiness but learning: implement a working agentic system, instrument it for observability, define evaluation metrics, and iterate on measurable improvements.

---

## Architecture Overview

```
News Sources → Ingestion Agent → Analysis Agent → Advisor Agent → User Response
                    ↓                  ↓                ↓
              [Observability Layer — traces, logs, metrics, evals]
```

### Agents

| Agent | Role |
|-------|------|
| **Ingestion Agent** | Fetches and normalizes financial news from external sources |
| **Analysis Agent** | Extracts entities, sentiment, and market signals from news |
| **Advisor Agent** | Synthesizes analysis into personalized financial advice |
| **Evaluator** | Scores responses on accuracy, relevance, and safety |

---

## Development Guidelines

### Language & Stack

- Python 3.11+
- Use the **Anthropic SDK** (`anthropic`) for all LLM calls — never use OpenAI or other providers unless explicitly told
- Default model: `claude-sonnet-4-6` unless a task requires reasoning depth (`claude-opus-4-8`) or speed (`claude-haiku-4-5-20251001`)

### Agentic Patterns

- Prefer **tool use** over prompt chaining for structured outputs
- Each agent must log its inputs and outputs for traceability
- Use `anthropic.Anthropic()` client directly — avoid LangChain or LlamaIndex abstractions

### Observability (non-negotiable)

Every agent call must emit:
1. A structured **log entry** (JSON) with: `agent_name`, `input_tokens`, `output_tokens`, `latency_ms`, `model`, `timestamp`
2. A **trace span** that captures the full input/output payload
3. Any **evaluation score** when a ground-truth or rubric is available

### Evaluation

- Define rubrics before implementing agents, not after
- Use LLM-as-judge for qualitative scoring
- Track scores across iterations in `evals/results/` to make improvements measurable

### Code Style

- No comments explaining what code does — only why when non-obvious
- No mock data for agents — use real or realistic news sources
- Keep each agent in its own module under `src/agents/`
- Tests go in `tests/` with a matching structure

---

## Project Structure

```
agentic-finantial-advisor/
├── src/
│   ├── agents/
│   │   ├── ingestion.py
│   │   ├── analysis.py
│   │   └── advisor.py
│   ├── tools/
│   ├── observability/
│   │   ├── logger.py
│   │   └── tracer.py
│   └── evals/
│       ├── rubrics/
│       └── results/
├── tests/
├── notebooks/          # Exploration and analysis
├── data/               # Raw and processed news samples
├── CLAUDE.md
└── README.md
```

---

## Key Goals (in priority order)

1. **Working pipeline** — end-to-end from news to advice
2. **Fully observable** — every agent step is logged and traced
3. **Evaluable** — quantitative scores exist for each run
4. **Improvable** — baseline vs. improved comparison is the deliverable
