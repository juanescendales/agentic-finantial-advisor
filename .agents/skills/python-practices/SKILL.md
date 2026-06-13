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

**The north star: write the simplest code that solves the problem today.**
Every abstraction, pattern, class, and layer has a cost. Only pay that cost when the
benefit is concrete and present — not hypothetical. When in doubt, stay flat.

Apply these rules every time you write or modify Python code.

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

## 3. SOLID — Diagnostic Tools, Not Construction Mandates

Use SOLID to **diagnose existing pain**, not to pre-emptively add structure.
Before applying any principle, ask: "Is this pain real right now, or am I anticipating it?"

**S — Single Responsibility:** A class doing too many unrelated things is a signal to split.
Don't split preemptively — wait until a class is actually hard to read or change.

**O — Open/Closed:** Relevant when you have proven variation points.
Don't create extension seams for imagined futures.

**L — Liskov Substitution:** Applies when you already have multiple implementations.
If there's only one, the contract question is moot.

**I — Interface Segregation:** Keep `Protocol`s small when you already need them.
Don't create a `Protocol` just to have one.

**D — Dependency Inversion:** Inject dependencies when you need to swap or test them.
A single concrete dependency that never changes doesn't need inversion.

```python
# Premature — one implementation, no test that needs a double
class AnalysisUseCase:
    def __init__(self, repo: NewsRepository) -> None:
        self.repo = repo

# Appropriate at this stage
class AnalysisUseCase:
    def __init__(self) -> None:
        self.repo = NewsRepository()
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

## 5. GRASP — Use to Diagnose, Not to Design Upfront

GRASP principles are most useful when reading existing code and noticing something feels wrong.
Don't design to GRASP from scratch — let the code grow and apply these when you feel friction.

**Information Expert:** If a use case is computing something an entity already has the data for, that's a smell.
**Low Coupling / High Cohesion:** If a change in one file ripples to five others, that's a signal — not a reason to add layers preemptively.
**Controller:** Routers should delegate, not contain logic. But don't create a use case layer until there's actual logic to separate.

---

## 6. Ports and Adapters — Earn the Abstraction

**Default to a plain class.** A port + adapter split only makes sense when at least one of
these is true today, not hypothetically:

1. There are (or will be) **multiple concrete implementations** in the same codebase.
2. Tests **require a fake** because the real implementation is slow, flaky, or has side effects.

If neither applies — you have one provider and no test that needs a double — a plain class is
the right call. Don't introduce a `Protocol` to make the code "feel" like clean architecture.

```python
# Fine when Anthropic is the only provider and tests call it directly
class LLMClient:
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

When the split *is* warranted, define the `Protocol` in `ports/` and the implementation in
`adapters/`. The use case imports only the protocol; tests inject a fake.

**Suggest the split, don't impose it.** If you see a reason the abstraction will pay off soon,
say so explicitly — e.g., "a second provider is planned" or "this blocks unit tests." Let the
team decide. Never add a port just because there is I/O.

---

## 7. Design Patterns — Last Resort, Not First Instinct

A plain function is better than a class. A plain class is better than a pattern.
Only reach for a pattern when the plain solution has a concrete, observable problem.

| Pattern | Only when... |
|---------|-------------|
| **Strategy** | You are *actually* swapping algorithms at runtime today |
| **Factory** | Creation logic is *already* complex enough to be confusing inline |
| **Observer / Event** | Multiple *existing* things need to react to the same event |
| **Decorator** | Cross-cutting behavior can't be added any other way |
| **Template Method** | You have *proven* duplication in a step sequence |

When you feel the pull toward a pattern, ask: "Can I solve this with a function or a plain class?"
If yes, do that. Name the pattern in a comment only if the indirection would otherwise confuse a reader.

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
- [ ] Could this be a function instead of a class? A module instead of a package?
- [ ] Every class, layer, and abstraction has a concrete reason to exist *right now*
- [ ] I/O dependencies are behind a `Protocol` only if there are multiple implementations or tests need a fake — otherwise a plain class is fine
- [ ] No logic duplicated from another file
- [ ] Nothing implemented "for the future" that isn't needed today
- [ ] If you added a pattern or layer, can you name the specific pain it solves?
