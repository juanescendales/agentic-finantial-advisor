---
name: python-practices
description: >
  Apply Python best practices whenever touching, writing, or reviewing any .py file.
  Invoke this skill before writing any Python code, modifying an existing Python module,
  reviewing a Python function or class, or any time Python is mentioned in the task.
  Covers: strict typing, PEP 8, module separation to avoid circular imports, SOLID,
  DRY, KISS, YAGNI, GRASP, and design patterns like ports/adapters.
---

# Python Best Practices

Apply these rules every time you write or modify Python code. They are not optional —
they define the minimum standard for every file in this project.

---

## 1. Typing — Non-Negotiable

Every function must have type annotations on all parameters and the return type.
Every class attribute must be typed. `Any` is forbidden without an explicit comment
explaining why no better type is possible.

```python
# Always
def fetch(topic: str, limit: int = 10) -> list[Article]: ...

# Never
def fetch(topic, limit=10): ...
```

Use `mypy --strict`. Fix all errors before committing.

**Prefer specific types over broad ones:**
- `Sequence[str]` over `list` when you don't need mutability
- `Mapping[str, int]` over `dict` in function signatures
- `Protocol` over `ABC` for interfaces — it enables structural subtyping without inheritance coupling

**Use `TypeAlias` for complex or repeated types:**
```python
from typing import TypeAlias

SignalMap: TypeAlias = dict[str, list[float]]
```

---

## 2. Circular Imports — Solve at the Root

Circular imports signal a design problem, not a Python limitation.
**Never use lazy imports as a workaround.** Fix the structure instead.

The rule: dependencies flow **one direction only**.

```
domain/ ← use_cases/ ← adapters/
              ↑
           ports/
```

If module A imports from B and B imports from A, one of them belongs in a third module
that both can import from — usually `shared/` or `domain/`.

```
# Wrong: two modules importing each other
# analysis.py imports from advisor.py
# advisor.py imports from analysis.py

# Right: extract the shared concept
# shared/models.py defines Signal
# analysis.py imports Signal from shared/models
# advisor.py imports Signal from shared/models
```

When you feel the urge to add an import inside a function body to "break a cycle",
stop. Redesign instead.

---

## 3. SOLID

**S — Single Responsibility:** One class, one reason to change.
A class that fetches news AND parses it AND stores it has three reasons to change.
Split it.

**O — Open/Closed:** Extend behavior through new classes or injected dependencies,
not by editing existing ones. This is why ports exist.

**L — Liskov Substitution:** Any implementation of a `Protocol` must be
substitutable without breaking the caller. Don't override methods in a way that
changes their contract.

**I — Interface Segregation:** Keep `Protocol`s small and focused.
A `NewsSource` protocol with one method is better than a `DataManager` with six.

**D — Dependency Inversion:** Use cases depend on protocols, never on concrete adapters.
Inject dependencies; never instantiate I/O objects inside business logic.

```python
# Wrong
class AnalysisUseCase:
    def __init__(self) -> None:
        self.repo = PostgresNewsRepository()  # concrete, untestable

# Right
class AnalysisUseCase:
    def __init__(self, repo: NewsRepository) -> None:  # protocol, injectable
        self.repo = repo
```

---

## 4. DRY, KISS, YAGNI

**DRY (Don't Repeat Yourself):** If the same logic appears twice, extract it.
If three files import and re-implement the same transformation, it belongs in `shared/`.

**KISS (Keep It Simple):** Write the simplest thing that works.
No metaclasses, no decorators, no clever tricks unless the problem genuinely requires them.
Simple code is readable code; readable code is maintainable code.

**YAGNI (You Aren't Gonna Need It):** Don't write the plugin system today because
you *might* need it next month. Build what the current requirement asks for.
Abstractions earn their complexity; they are not free.

---

## 5. GRASP — Who Owns What

**Information Expert:** Assign responsibility to the class that has the data.
An `Article` knows its own word count; a use case should not compute it.

**Creator:** The class that aggregates or closely uses an object should create it.
A `NewsIngestionUseCase` creates `Article` objects; a router does not.

**Low Coupling:** Minimize how many things a class depends on.
If changing one module forces changes in five others, something is coupled wrong.

**High Cohesion:** Keep things that change together, together.
Everything in `ingestion/` belongs to ingestion. If it doesn't, move it.

**Controller:** Use cases are the controllers. Routers delegate to them; they don't do logic themselves.

---

## 6. Ports and Adapters — Use When There Is I/O

Any time a use case needs to talk to the outside world (HTTP, DB, file system, LLM API),
define a `Protocol` in `ports/` and a concrete implementation in `adapters/`.

```python
# src/ports/llm_client.py
from typing import Protocol

class LLMClient(Protocol):
    def complete(self, prompt: str) -> str: ...


# src/adapters/anthropic_adapter.py
import anthropic

class AnthropicAdapter:
    def __init__(self, model: str) -> None:
        self._client = anthropic.Anthropic()
        self._model = model

    def complete(self, prompt: str) -> str:
        msg = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
```

The use case only knows `LLMClient`. Tests inject a fake. Production injects `AnthropicAdapter`.
Zero changes to business logic when switching providers.

---

## 7. Design Patterns — Apply With Intention

Use patterns when they solve a real, present problem — not to make the code look architectural.

| Pattern | When to use it |
|---------|---------------|
| **Strategy** | You need to swap an algorithm at runtime (e.g., different scoring rubrics) |
| **Factory** | Object creation logic is complex or depends on config |
| **Observer / Event** | One thing happens and multiple things need to react |
| **Decorator** | Add cross-cutting behavior (logging, retry) without modifying the target |
| **Template Method** | You have a fixed skeleton with variable steps |

If you can solve the problem with a plain function and a `Protocol`, do that first.
Reach for patterns when the plain solution starts to hurt.

---

## 8. PEP 8 Essentials

- 4 spaces, no tabs
- Max line length: 88 characters (Black default)
- Two blank lines between top-level definitions, one inside a class
- Imports: stdlib → third-party → local, each group separated by a blank line
- Name things: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants
- No wildcard imports (`from module import *`)

Run `black` and `ruff` before every commit. If they change something, understand why.

---

## Quick Checklist Before Saving a File

- [ ] All functions and methods have full type annotations
- [ ] `mypy --strict` passes on this file
- [ ] No import inside a function body to avoid circular dependency
- [ ] No class has more than one reason to change
- [ ] Every I/O dependency is behind a `Protocol`
- [ ] No logic duplicated from another file
- [ ] Nothing implemented "for the future" that isn't needed today
