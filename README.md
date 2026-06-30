# BizOS — AI Operating System for Entities

[![Version](https://img.shields.io/badge/version-v6.0.0-blue.svg)](https://github.com/your-org/bizos/releases)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-367%20passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-78%25-yellow.svg)](htmlcov/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **BizOS is not a chatbot, a dashboard, or a workflow tool.** It is a foundational AI Operating System — a platform that understands an entity, builds a persistent digital model of it, and autonomously orchestrates AI agents to help it achieve its goals through planning, reasoning, memory, and execution.

---

## Architecture

BizOS v6.0.0 is organized around two frozen, production-grade kernels that communicate only through a strictly-typed bridge interface.

`
Executive Intelligence Kernel (M6)
Intake → Strategy → Decision → Oversight → Learning → Workspaces
                          |
                   Runtime Bridge  (one-way boundary)
                          |
Runtime OS Kernel (M5)
Agents → Capabilities → Tasks → Scheduler → Budget → Session
                          |
Infrastructure Layer
AI Kernel · PostgreSQL · Qdrant · Cache
`

### Boundary Contracts

| Boundary | Rule |
|----------|------|
| Intelligence → Runtime | Allowed **only** through runtime_bridge/ |
| Runtime → Intelligence | Forbidden |
| Interfaces → Kernels | Inward only |
| Infrastructure → Kernels | Never |

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Runtime | Python 3.12+, asyncio |
| API Framework | FastAPI 0.115+ |
| Domain Modeling | Pydantic v2 |
| AI Provider | Google Gemini (primary, extensible) |
| Persistence | PostgreSQL via Supabase |
| Vector Store | Qdrant |
| Logging | Structlog |
| Testing | Pytest + Hypothesis + Syrupy |
| Package Manager | uv |

---

## Project Structure

`
bizos/
├── app/
│   ├── bootstrap/          # Dependency composition and wiring
│   ├── core/               # OperationContext (cross-cutting concerns)
│   ├── infrastructure/     # AI, persistence, vectorstore, cache
│   ├── intelligence/       # M6 Executive Intelligence Kernel [FROZEN]
│   │   ├── core/
│   │   ├── decision/       # Planning and recommendation engines
│   │   ├── intake/         # Intent classification and context assembly
│   │   ├── learning/       # Memory, cognitive trace, outcome tracking
│   │   ├── oversight/      # Governance and compliance
│   │   ├── runtime_bridge/ # Only approved Runtime integration channel
│   │   ├── strategy/       # Goal management and strategy formation
│   │   └── workspaces/
│   ├── interfaces/         # HTTP API, CLI (planned), SDK (planned)
│   ├── platform/           # Config, DI, telemetry, resilience
│   ├── runtime/            # M5 Runtime OS Kernel [FROZEN]
│   │   ├── agents/
│   │   ├── budget/
│   │   ├── capabilities/
│   │   ├── policies/
│   │   ├── queues/
│   │   ├── retry/
│   │   ├── scheduler/
│   │   ├── session/
│   │   └── tasks/
│   └── shared/             # Universal primitives (enums, events, exceptions)
├── docs/
│   ├── adr/                # Architecture Decision Records
│   ├── architecture/       # System architecture documentation
│   ├── developer/          # Developer guides and API references
│   ├── milestones/         # Milestone completion summaries
│   └── operations/         # Deployment and operations guides
├── migrations/             # SQL schema migration scripts
├── scripts/                # Developer utilities
├── tests/                  # Test suite (mirrors app/ exactly)
├── .env.example
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── pyproject.toml
└── README.md
`

---

## Getting Started

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- Supabase project (PostgreSQL)
- Qdrant instance (local Docker or cloud)

### Installation

`ash
git clone https://github.com/your-org/bizos.git
cd bizos
uv sync
cp .env.example .env
# Edit .env with your Supabase URL, API key, and Gemini API key
`

### Running the API

`ash
docker-compose up -d
uv run uvicorn app.main:app --reload
curl http://localhost:8000/health
`

### Running Tests

`ash
uv run pytest                                    # Full suite
uv run pytest --cov=app --cov-report=html        # With coverage
uv run pytest tests/runtime/                     # Runtime layer only
uv run pytest tests/intelligence/               # Intelligence layer only
uv run pytest tests/certification/              # E2E certification
`

---

## Milestone History

| Milestone | Description | Status |
|-----------|-------------|--------|
| M0 | Project Foundation | ✅ Complete |
| M1 | Digital Twin Foundation | ✅ Complete |
| M2 | Memory Engine | ✅ Complete |
| M3 | AI Kernel & Provider Abstraction | ✅ Complete |
| M4 | Context Engine | ✅ Complete |
| M5 | Runtime OS Kernel | ✅ **Frozen** |
| M6 | Executive Intelligence Kernel | ✅ **Frozen** |

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture Overview](docs/architecture/index.md) | System-wide architecture reference |
| [AI Kernel](docs/architecture/Ai_Kernel.md) | AI provider abstraction and kernel design |
| [Memory Engine](docs/architecture/Memory_Engine.md) | Semantic memory architecture |
| [Developer Guide](docs/developer/API_Reference.md) | API reference and integration |
| [Configuration](docs/developer/Configuration_Reference.md) | Environment variables and settings |
| [Testing Strategy](docs/developer/Testing_Strategy.md) | Test architecture and conventions |
| [Operations Runbook](docs/operations/RUNBOOK.md) | Deployment and operational procedures |
| [ADR Catalog](docs/adr/) | Architecture Decision Records |

---

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting pull requests.

## Security

Please read [SECURITY.md](SECURITY.md) for our vulnerability disclosure policy.

## License

MIT License — see [LICENSE](LICENSE) for details.
