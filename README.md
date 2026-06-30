# BizOS

> **An AI Operating System for Businesses, Organizations, and Digital Entities**

[![Version](https://img.shields.io/badge/version-v6.0.0-blue.svg)](https://github.com/your-org/bizos/releases)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-367%20passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-78.5%25-yellow.svg)](htmlcov/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## What is BizOS?

Today's AI assistants can answer questions.

Tomorrow's AI systems will run organizations.

BizOS is an AI Operating System built for that future.

It continuously understands an entity, remembers what matters, reasons about goals, plans complex work, coordinates execution, and learns from every outcome—allowing autonomous AI systems to operate with persistent intelligence instead of isolated conversations.

---

## Core Philosophy

BizOS separates **thinking** from **execution**.

```
Think
   ↓
Plan
   ↓
Decide
   ↓
Execute
   ↓
Learn
```

Executive reasoning never performs execution directly.

Execution never performs reasoning.

This separation is enforced through a strictly typed Runtime Bridge.

---

# Architecture

```
                           User
                             │
                             ▼
              Interfaces (HTTP / CLI / SDK)
                             │
                             ▼
        ┌────────────────────────────────────┐
        │ Executive Intelligence Kernel (M6) │
        │                                    │
        │  • Intake                          │
        │  • Strategy                        │
        │  • Decision                        │
        │  • Oversight                       │
        │  • Learning                        │
        │  • Workspaces                      │
        └──────────────┬─────────────────────┘
                       │
              Runtime Bridge
        (Only Approved Integration Point)
                       │
        ┌──────────────▼─────────────────────┐
        │      Runtime Kernel (M5)           │
        │                                    │
        │  • Scheduler                       │
        │  • Tasks                           │
        │  • Agents                          │
        │  • Capabilities                    │
        │  • Budget                          │
        │  • Session                         │
        └──────────────┬─────────────────────┘
                       │
                       ▼
              Infrastructure Layer

      AI Providers • PostgreSQL • Qdrant • Cache
```

---

## Architectural Contracts

| Rule | Status |
|------|--------|
| Intelligence never executes tasks directly | ✅ |
| Runtime never performs reasoning | ✅ |
| Runtime Bridge is the only integration point | ✅ |
| Infrastructure never depends on Intelligence | ✅ |
| Interfaces depend inward only | ✅ |
| Runtime and Intelligence remain independently testable | ✅ |

---

# Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12+ |
| Runtime | asyncio |
| API | FastAPI |
| Validation | Pydantic v2 |
| AI Providers | Google Gemini (primary), extensible |
| Database | PostgreSQL (Supabase) |
| Vector Store | Qdrant |
| Logging | Structlog |
| Testing | Pytest, Hypothesis, Syrupy |
| Package Manager | uv |

---

# Project Structure

```text
bizos/
├── app/
│   ├── bootstrap/
│   ├── core/
│   ├── infrastructure/
│   ├── intelligence/
│   ├── interfaces/
│   ├── platform/
│   ├── runtime/
│   └── shared/
├── docs/
├── migrations/
├── scripts/
├── tests/
├── README.md
└── pyproject.toml
```

### Directory Overview

| Directory | Purpose |
|-----------|---------|
| `app/intelligence` | Executive Intelligence Kernel (M6) |
| `app/runtime` | Runtime Execution Kernel (M5) |
| `app/infrastructure` | AI providers, persistence, cache, vector store |
| `app/interfaces` | HTTP API, CLI, SDK |
| `app/platform` | Configuration, telemetry, resilience |
| `app/shared` | Shared primitives |
| `tests` | Mirrors the application structure |
| `docs` | Architecture, ADRs, developer guides |

---

# Getting Started

## Prerequisites

- Python 3.12+
- uv
- Supabase
- Qdrant

## Installation

```bash
git clone https://github.com/your-org/bizos.git

cd bizos

uv sync

cp .env.example .env
```

Configure your environment variables.

## Run

```bash
docker compose up -d

uv run uvicorn app.main:app --reload
```

Health check:

```bash
curl http://localhost:8000/health
```

---

# Testing

Run all tests:

```bash
uv run pytest
```

Coverage:

```bash
uv run pytest --cov=app --cov-report=html
```

Runtime only:

```bash
uv run pytest tests/runtime/
```

Intelligence only:

```bash
uv run pytest tests/intelligence/
```

Certification:

```bash
uv run pytest tests/certification/
```

---

# Milestones

| Milestone | Status |
|-----------|--------|
| M0 | ✅ Completed |
| M1 | ✅ Completed |
| M2 | ✅ Completed |
| M3 | ✅ Completed |
| M4 | ✅ Completed |
| M5 | ✅ Completed |
| M6 | ✅ Completed |

---

# Documentation

- 📘 Architecture
- 📗 Developer Guide
- 📙 Operations
- 📕 ADR Catalog
- 📓 Configuration
- 📔 Testing Strategy

---

# Contributing

Please read **CONTRIBUTING.md** before opening a pull request.

---

# Security

Please read **SECURITY.md** before reporting vulnerabilities.

---

# License

Released under the MIT License.
