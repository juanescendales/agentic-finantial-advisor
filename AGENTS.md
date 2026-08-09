## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.


---

## Project: Agentic Financial Advisor

Educational project that simulates a **news-driven financial advising system** built as an observable and evaluable multi-agent pipeline. The primary goal is not production readiness but learning: implement a working agentic system, instrument it for observability, define evaluation metrics, and iterate on measurable improvements.

### Architecture

```
News Sources → Ingestion Agent → Analysis Agent → Advisor Agent → User Response
                    ↓                  ↓                ↓
              [Observability Layer — traces, logs, metrics, evals]
```

| Agent | Role |
|-------|------|
| **Ingestion Agent** | Fetches and normalizes financial news from external sources |
| **Analysis Agent** | Extracts entities, sentiment, and market signals from news |
| **Advisor Agent** | Synthesizes analysis into personalized financial advice |
| **Evaluator** | Scores responses on accuracy, relevance, and safety |

### Language & Stack

- Python 3.11+
- Use **OpenRouter** via the `openai` SDK — never use other providers unless explicitly told
- Client: `openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])`
- Default model: `openai/gpt-oss-20b:free` unless the task requires speed (`mistralai/mistral-7b-instruct:free`)
- Free OpenRouter models confirmed to support `structured_outputs` (required for `response_format` json_schema), worth comparing across providers:
  - `openai/gpt-oss-20b:free` (OpenAI)
  - `google/gemma-4-26b-a4b-it:free` (Google)
  - `nvidia/nemotron-3-super-120b-a12b:free` (NVIDIA, largest/most capable of the four)
  - `nvidia/nemotron-nano-9b-v2:free` (NVIDIA, smallest/lightweight contrast)
- Avoid LangChain or LlamaIndex abstractions
- Prefer **structured/tool-based extraction** (function calling or `response_format` json_schema) over parsing free-text model output

### Observability (non-negotiable)

This is required project infrastructure — it takes precedence over Simplicity First. Every agent call must emit:
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

### Project Structure

```
agentic-finantial-advisor/
├── app/
├── docs/
├── src/
│   ├── agents/
│   │   ├── ingestion.py
│   │   ├── analysis.py
│   │   └── advisor.py
│   ├── tools/
│   ├── observability/
│   │   ├── logger.py
│   │   └── tracer.py
├── tests/
│   ├── evals/
│       ├── rubrics/
│       └── results/
├── notebooks/
├── data/
├── AGENTS.md
├── CLAUDE.md
└── README.md
```

### Priority Order

Working pipeline → fully observable → evaluable → improvable (baseline vs. improved comparison is the deliverable).