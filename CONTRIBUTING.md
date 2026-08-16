# Contributing to BizOS

Thank you for your interest in contributing to BizOS — the AI Operating System for Entities.

BizOS is a production-grade platform built around two frozen kernels (M5 Runtime, M6 Intelligence).
Our standards for architecture, testing, and documentation reflect that quality bar.

---

## Quick Start

```bash
git clone https://github.com/your-org/bizos.git
cd bizos
uv sync
cp .env.example .env
uv run pytest         # must pass before you start
```

---

## Architectural Rules

**These are hard rules, not guidelines:**

| Rule | Detail |
|------|--------|
| **Never modify frozen kernels** | `app/runtime/` and `app/intelligence/` are frozen. Changes require principal architect sign-off. |
| **No cross-kernel imports** | `runtime` may never import from `intelligence`. Reverse is allowed only via `runtime_bridge/`. |
| **No business logic in infrastructure** | `app/infrastructure/` adapts external systems. Domain logic belongs in the kernels. |
| **Models stay in their context** | Domain models live beside the code that owns them, not in `app/shared/`. |
| **Tests mirror production** | Every production package has a corresponding test package at the same path under `tests/`. |

---

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Stable. Never commit directly. |
| `feat/*` | New features (`feat/cli-interface`) |
| `fix/*` | Bug fixes (`fix/budget-overflow`) |
| `docs/*` | Documentation only |
| `chore/*` | Dependency updates, tooling |

---

## Coding Standards

- **Typing**: All code must be fully typed. Use `from __future__ import annotations` + `TYPE_CHECKING` for forward references.
- **Logging**: Always use `structlog`. Never use `print()` or `logging.getLogger()` directly.
- **AI calls**: Never call a provider directly. Always go through `AbstractAIKernel`.
- **Formatting**: Run `uv run ruff check . --fix` before committing.

---

## Commit Conventions

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add CLI interface scaffold
fix: correct budget overflow in BudgetManager
docs: update ADR-001 with dual-kernel rationale
chore: upgrade pydantic to 2.11.0
test: add property tests for SchedulerPolicy
```

---

## Pull Request Checklist

- [ ] All existing tests pass: `uv run pytest`
- [ ] New code has test coverage in the correct `tests/` mirror package
- [ ] Ruff reports no errors: `uv run ruff check app/ tests/`
- [ ] Architecture boundaries respected (no cross-kernel imports)
- [ ] Relevant `docs/` updated if behavior or interfaces changed
- [ ] CHANGELOG.md entry added under `[Unreleased]`

---

## Testing Requirements

| Change Type | Required Tests |
|------------|----------------|
| New domain logic | Unit tests in mirrored `tests/` package |
| New infrastructure adapter | Integration test |
| New HTTP endpoint | Interface test in `tests/interfaces/` |
| Cross-kernel change | Certification test in `tests/certification/` |

---

## Documentation Requirements

- New subsystems: add entry to `docs/architecture/index.md`
- Major design decisions: add an ADR to `docs/adr/`
- New capabilities: update relevant milestone summary in `docs/milestones/`
