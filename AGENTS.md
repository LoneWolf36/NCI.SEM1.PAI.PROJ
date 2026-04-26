# Repository Guidelines

## Architecture Principles

### YAGNI (You Aren't Gonna Need It)
- Build only what is needed today
- If a feature is not referenced by a cavekit requirement, do not build it

### Simplicity First
- Prefer the simplest solution that meets the acceptance criteria
- If a solution needs explanation, it's probably too complex

## Cavekit — Spec-Driven Development

Domain kits live in `context/kits/`. See `context/kits/cavekit-overview.md` for the domain index.

### Workflow

```
/ck:sketch   → Decompose into domains with R-numbered requirements
/ck:map      → Generate tiered build plan
/ck:make     → Autonomous build loop
/ck:check    → Gap analysis and peer review
```
