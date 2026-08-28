# PASTA-ELN and LLM assistant — design discussion

Status: discussion design; not an implementation commitment.

## Product direction

PASTA-ELN should become a dual-interface scientific workspace. Its existing
structured UI remains a first-class way to browse, inspect, edit, and orient
within projects, samples, experiments, files, and relations. An LLM assistant
is a connected second interface for describing intent, synthesising context,
discussing interpretations, and preparing work.

The assistant and UI must work as one workspace. Assistant responses should
open the relevant object in the UI; the scientist can inspect the underlying
record directly. Proposed durable changes are presented in an ELN-aware review
surface, analogous to Codex's diff and editor integration.

Scientific work is a continuous loop:

```text
past records → interpretation → next experimental intent
     ↑                                      ↓
     └──── new observations and documentation ────┘
```

The assistant helps maintain that continuity, rather than splitting “looking
back” from “doing today's work” into separate products.

## First implementation: ephemeral assistant session

The first assistant is one session per open PASTA-ELN window. It has a
conversation history only for the lifetime of that session. Closing the window
ends the thread; there is no general conversation history, branching, or
thread data model in this phase.

The assistant automatically receives the selected UI object and its immediate
context. The scientist can explicitly add or pin broader context—for example,
another experiment, sample, result table, or file—when needed. “Reset
conversation” clears the assistant's temporary working context, not ELN data.

The durable outcome of a discussion is an accepted ELN record, linked file,
analysis, draft, or other existing project artifact. The session itself is not
a scientific object in the first phase.

## Deferred lightweight continuity

If restarting with no conversational continuity proves limiting, introduce one
compact context file in each project's on-disk directory. The name is
intentionally provisional, for example `.llm-compact`. The project's existing
document type / identity provides the association; no new global thread
hierarchy is required.

At the start of an assistant session, PASTA-ELN reads this compact project
context. At the end of the session, it rewrites it with a concise updated
summary. This file is a lightweight hand-off between sessions, not a raw turn
log and not a branched conversation store. Its exact format, location, and
inclusion in project export remain decisions for that later phase.

## Deliberately deferred

- Persistent full turn histories.
- Conversation branches and merging.
- A standalone assistant-centric replacement for the current UI.
- A new conversation object in the core ELN data model.

## Next prototype

Build the in-window, ephemeral session with selected-object context, explicit
context pinning, UI deep links, and a visible proposal/review surface. Learn
whether that interaction reduces the scientist's effort to reconstruct context
and makes the UI more useful during active research. Only then decide whether
the project-local compact context file is needed.
