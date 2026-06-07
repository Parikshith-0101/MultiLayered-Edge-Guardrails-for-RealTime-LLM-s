---
trigger: always_on
---

# Agent Coding Rules & Technical Guardrails

## 1. Architectural Integrity

- Maintain strict separation of concerns between Track A (Guardrails Engine) and Track B (Backend API).
- Track A ("guardrails/") must remain a pure, standalone Python library containing only validation logic.
- NEVER import backend framework modules (FastAPI, Uvicorn, LiteLLM) inside Track A core files.
- All inter-module communication must occur through explicitly defined schemas inside "guardrails/schemas/data_models.py".
- Avoid circular dependencies.

---

## 2. Source of Truth Principles

- Never duplicate:
  - schemas
  - validation logic
  - constants
  - enums
  - configuration values

- If duplication is detected, consolidate into a shared source of truth.
- Any structural change must be reflected in the corresponding schema/model before dependent logic is modified.

---

## 3. Dependency Awareness

Before modifying any file:

- Identify direct imports.
- Identify downstream consumers.
- Verify interface compatibility.
- Understand the impact radius of the change.

Never modify a public contract without documenting the impact.

---

## 4. Incremental & Safe Development

Before implementing production logic:

- Create or verify a functional skeleton.
- Preserve interface compatibility.
- Ensure dependent modules remain unblocked.

Placeholder implementations should:

- return safe defaults
- be clearly marked as temporary
- never silently mask critical failures

---

## 5. Code Quality Standards

- Use complete type annotations throughout the codebase.
- Avoid "Any" unless there is a justified reason.
- Keep functions focused on a single responsibility.
- Prefer readability over cleverness.

When a function becomes difficult to understand:

- extract helper functions
- reduce nesting
- separate concerns

---

## 6. Error Handling & Resilience

- Anticipate edge cases.
- Validate external inputs.
- Wrap external integrations in defensive error handling.
- Log meaningful failure information.
- Return predictable fallback responses where appropriate.

Avoid allowing unexpected exceptions to cascade across unrelated modules.

---

## 7. Testability

Design business logic so it can be tested independently from:

- APIs
- databases
- frameworks
- UI layers

Favor dependency injection and modular design where practical.

---

## 8. Documentation Standards

Write documentation that explains:

- why a decision was made
- architectural intent
- integration expectations
- known limitations

Avoid documentation that merely repeats code behavior.

Public services, business logic modules, and complex functions should contain meaningful docstrings.

- **Inline Comments:** Explain why a decision was made, not what the code is doing. Avoid redundant comments that merely restate the implementation.

---

## 9. Verification Mindset

Before considering work complete:

- Verify correctness.
- Verify schema/interface compatibility.
- Remove dead code, unused imports, and temporary artifacts.

---

## 10. Security & Defensive Thinking

When handling user-controlled input:

- Consider encoding tricks.
- Consider Unicode obfuscation.
- Consider nested payload formats.
- Consider malformed data structures.
- Consider validation bypass attempts.

Build validation systems defensively rather than assuming well-formed input.

---

## 11. Project Memory Preservation

The file "INTEGRATION_HANDOFF.md" is the persistent project knowledge base.

Before starting work:

- Read relevant sections.

After completing work:

- Update relevant sections.

Task completion is not finished until project documentation is updated.