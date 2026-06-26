# Contributing to BizOS

First off, thank you for considering contributing to BizOS! 

BizOS is an AI-Native Operating System for Entities. We are building the foundational infrastructure for agentic applications, meaning our architecture, testing, and documentation standards are rigorous.

## Development Setup

1. **Fork & Clone:** Fork the repository and clone it locally.
2. **Install `uv`:** We use `uv` for lightning-fast dependency management.
3. **Environment:** Run `uv sync --dev` to set up the environment and install testing dependencies.
4. **Pre-commit:** We use `ruff` for linting and formatting. Ensure you run `uv run ruff check .` before committing.

## Branch Strategy

* `main`: The stable branch. Do not commit directly to `main`.
* `feat/*`: For new features (e.g., `feat/intent-engine`).
* `fix/*`: For bug fixes (e.g., `fix/memory-leak`).
* `docs/*`: For documentation updates.

## Coding Standards

* **Strict Layering:** BizOS adheres to a strict layered architecture. **Never** import a repository into an API router. The flow is strictly: API -> Service -> Repository.
* **Typing:** All Python code must be strictly typed using modern `type` hints.
* **Logging:** Do not use print statements or standard `logging`. Always use `structlog` and bind the `OperationContext` for traceability.
* **AI Agnostic:** Never hardcode LLM prompts or provider-specific logic into domain services. Use the `AbstractAIKernel`.

## Commit Message Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/):

* `feat: added qdrant support`
* `fix: resolved duplicate events in bus`
* `docs: updated architecture diagrams`
* `chore: bumped dependency versions`

## Pull Request Process

1. Ensure all tests pass (`uv run pytest`).
2. Update relevant documentation in `docs/` if your change affects architecture or APIs.
3. Submit the PR with a clear description of the problem and your solution.
4. A maintainer will review your code. You may be asked to add architecture tests or chaos tests if you are altering core behavior.

## Testing Expectations

* Unit Tests are required for all new business logic.
* Integration Tests are required for any repository or API changes.
* **Architecture Tests:** If you add a new module, ensure it passes `tests/architecture/test_boundaries.py`.

## Documentation Expectations

We treat documentation as code. Do not duplicate information. If you add a subsystem, link it centrally from `docs/Architecture_Index.md`.
