---
description: Structured development workflow that enforces feature analysis, dependency mapping, architecture validation, implementation, verification, and continuous INTEGRATION_HANDOFF updates to ensure maintainable, consistent, and integration
---

# Agent Execution Workflow

## Workflow 1: Feature Implementation Lifecycle

### Step 1 — Analyze

- Understand the requested feature.
- Inspect the target files.
- Review relevant schemas, models, DTOs, and interfaces.
- Read relevant sections of "INTEGRATION_HANDOFF.md".

---

### Step 2 — Dependency Mapping

Before making changes:

- Identify imports.
- Identify dependent modules.
- Identify affected APIs.
- Identify affected schemas.
- Identify potential integration risks.

Document major impacts before implementation.

---

### Step 3 — Design Validation

Validate that the proposed implementation:

- follows project architecture
- preserves separation of concerns
- avoids unnecessary coupling
- does not duplicate existing functionality

Reuse existing components whenever possible.

---

### Step 4 — Skeleton Creation

If no implementation exists:

- Create typed function signatures.
- Create schema references.
- Create service structure.
- Add meaningful docstrings.

Maintain compatibility with future integrations.

---

### Step 5 — Production Implementation

Replace placeholders with production-ready logic.

Requirements:

- robust error handling
- edge-case awareness
- type-safe implementation
- maintainable structure
- minimal technical debt

---

### Step 6 — Verification

Verify:

- typing
- imports
- interfaces
- edge cases
- schema compatibility
- integration compatibility

Remove:

- dead code
- unused imports
- temporary debug statements

---

### Step 7 — Documentation Update

Purpose: Single detailed description file that must be continuously maintained and updated by the agent after completing each file, feature, or folder. This file acts as the primary handoff guide for backend implementors.

Immediately update "INTEGRATION_HANDOFF.md". 

When updating the document to explain folders and files, you MUST strictly adhere to the following hierarchical format:
- **Main Folder:** Objective/Purpose in one or two lines.
  - **Subfolder:** Objective of this specific folder.
    - **File Name:** Explain what it is doing exactly.
      - **i/p:** [Specify the exact input data type and structure]
      - **process:** [Specify the core algorithmic or filtering process occurring]
      - **o/p:** [Specify the exact output data type and structure returned]

Documentation updates are mandatory.

---

### Step 8 — Progress Summary

Provide a concise summary containing:

- files modified
- features completed
- integration impact
- pending work
- risks or technical debt

---

## Workflow 2: Safe Modification Path

When modifying existing functionality:

1. Preserve public interfaces whenever possible.
2. Preserve parameter names unless explicitly required.
3. Preserve expected return structures.
4. Update schemas before dependent logic when structural changes are necessary.
5. Verify downstream compatibility before finalizing changes.
6. Update "INTEGRATION_HANDOFF.md" immediately after modification.

No modification is considered complete until compatibility and documentation have been verified.