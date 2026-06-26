# BizOS — AI-Native Operating System for Entities

[![Version](https://img.shields.io/badge/version-v2.0.0-blue.svg)](https://github.com/your-org/bizos/releases)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **BizOS is not a chatbot, a dashboard, or a CRM.** It is a foundational AI Operating System designed to understand an entity, build a digital twin of it, and help it achieve its goals through planning, reasoning, memory, simulation, and autonomous execution.

---

## 🌟 Project Vision

The future of AI is not conversational—it is agentic and autonomous. BizOS provides the architectural foundation for AI agents to possess persistent memory, robust state management, and provider-agnostic cognitive capabilities. 

By modeling businesses, individuals, or systems as **Digital Twins**, BizOS allows AI to step out of the chat window and seamlessly integrate into real-world operational logic.

## 🚀 Why BizOS?

* **AI-Native from Day One:** Built specifically for LLM and vector-based operations.
* **Provider Agnostic Kernel:** Swap between Gemini, OpenAI, or Local LLMs without rewriting business logic.
* **Event-Driven Resilience:** Asynchronous background processing backed by Tenacity loops.
* **Strict Layered Architecture:** Enterprise-grade separation of API, Services, Repositories, and Providers.

## 🧠 Key Features

* **Digital Twin Management:** Track the state, metadata, and history of any modeled entity.
* **Semantic Memory Engine:** Embed, store, and semantically search a Twin's contextual experiences.
* **Event Bus:** Decoupled memory summarization and vector processing pipelines.
* **Qdrant Vector Integration:** High-performance semantic indexing.

## 🏗 Architecture Overview

BizOS adheres to a strict Layered Architecture combined with Domain-Driven concepts.

> **[View Architecture Index](docs/Architecture_Index.md)** for deep dives into individual subsystems.

*(Recommended: Add Architecture Diagram Screenshot here)*

## 🛠 Technology Stack

* **Core:** Python 3.12+, FastAPI, Pydantic v2
* **Database:** PostgreSQL (via Supabase)
* **Vector Store:** Qdrant
* **AI Providers:** Google Gemini (Primary), extensibility for others
* **Resilience:** Tenacity, Structlog

## 📁 Project Structure

```text
bizos/
├── app/
│   ├── api/v1/         # Versioned REST endpoints
│   ├── core/           # Operation context and config
│   ├── events/         # Event Bus and Handlers
│   ├── models/         # DTOs, schemas, and enums
│   ├── repositories/   # Persistence (Supabase, Qdrant)
│   ├── services/       # Business logic (Memory, Twins, AI Kernel)
│   └── workers/        # Background processing
├── docs/               # Architecture and operational documentation
├── migrations/         # SQL Schema migrations
├── tests/              # E2E, Integration, Unit, and Chaos tests
```

## ⚙️ Installation

BizOS uses [`uv`](https://github.com/astral-sh/uv) for lightning-fast dependency management.

1. Ensure Python 3.12+ is installed.
2. Install dependencies:
   ```bash
   uv sync
   # Or using standard pip:
   pip install -e ".[dev]"
   ```
3. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```

## 🚦 Quick Start

1. **Start Infrastructure:**
   Ensure you have your Supabase credentials in `.env`, then start Qdrant locally:
   ```bash
   docker-compose up -d
   ```

2. **Run the API Server:**
   ```bash
   uv run uvicorn app.main:app --reload
   ```

3. **Verify Health:**
   Check the sub-system health at `http://localhost:8000/api/v1/health/memory` or view the Swagger UI at `http://localhost:8000/docs`.

## 🗺 Roadmap

* **Milestone 1:** Digital Twin Foundation ✅
* **Milestone 2:** Memory Engine (v2.0.0) ✅
* **Milestone 3:** Goals & Intent Engine ⏳ (Next)
* **Milestone 4:** Agent Swarms & Delegation
* **Milestone 5:** Temporal Simulation Reality

## 🤝 Contributing

We welcome contributions from the community! Please read our [Contributing Guide](CONTRIBUTING.md) to understand our development process, branching strategy, and coding standards.

## 🛡 Security

Please review our [Security Policy](SECURITY.md) for information on reporting vulnerabilities and our disclosure policy.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
