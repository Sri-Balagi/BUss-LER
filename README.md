# BizOS

> **An AI Operating System for Businesses, Organizations, and Digital Entities**

[![Version](https://img.shields.io/badge/version-v6.0.0--wave14-blue.svg)](https://github.com/your-org/bizos/releases)
[![AI OS Maturity](https://img.shields.io/badge/maturity-Level%205%20Autonomous%20AI%20OS-purple.svg)](impossible_edge_case_report.md)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-522%20certified%20matrix-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-100%25%20matrix%20pass-green.svg)](htmlcov/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## What is BizOS?

Today's AI assistants can answer questions.

Tomorrow's AI systems will run organizations.

**BizOS is an AI Operating System built for that future.**

It continuously understands an entity, remembers what matters, reasons about goals, plans complex work, coordinates execution, and learns from every outcome—allowing autonomous AI systems to operate with persistent intelligence instead of isolated conversations.

---

## Core Philosophy: The Dual-Kernel Architecture

BizOS separates **thinking** from **execution** through two frozen, independently testable kernels communicating exclusively via an enforced one-way typed gateway:

```
Think  (Executive Intelligence Kernel — M6 — FROZEN)
   ↓
Plan   (Strategic Planning & Recommendation Engines)
   ↓
Decide (Decision Rationale & Compliance Governance)
   ↓      === RUNTIME BRIDGE (Strictly Typed Gateway) ===
Execute (Runtime OS Kernel — M5 — FROZEN)
   ↓
Learn  (Semantic Memory & Cognitive Trace Evolution)
```

1. **Executive Reasoning never performs execution directly.**
2. **Execution never performs reasoning.**
3. **The Runtime Bridge is the only authorized cross-kernel integration point.**

---

# Architecture Overview

```
                                 ┌─────────────────────────────────────────────────────────────────────────────┐
                                 │                                ENTITY                                       │
                                 │                  Business • Organization • Individual                       │
                                 └─────────────────────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       ▼
                                 ┌─────────────────────────────────────────────────────────────────────────────┐
                                 │                    DIGITAL REPRESENTATION LAYER (M1)                        │
                                 │  • Digital Twin State         • Entity Identity & Snapshot History          │
                                 │  • Digital Twin Drift Engine  • Supabase PostgreSQL Persistence             │
                                 └─────────────────────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       ▼
                                 ┌─────────────────────────────────────────────────────────────────────────────┐
                                 │                 KNOWLEDGE & MEMORY ENGINE LAYER (M2 / M4)                   │
                                 │  • Business Knowledge Graph   • Qdrant Semantic Memory & Embeddings          │
                                 │  • Episodic & Working Memory  • Cognitive Traces & Audit Trails             │
                                 └─────────────────────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       ▼
                                 ┌─────────────────────────────────────────────────────────────────────────────┐
                                 │                EXECUTIVE INTELLIGENCE KERNEL (M3 / M6 — FROZEN)             │
                                 │  • Intent Classification      • EnterpriseContext Assembly                  │
                                 │  • Strategic Goal Manager     • AI Planning & Recommendation Engine         │
                                 │  • Governance & Compliance    • Workspace Isolation & Audit Logs            │
                                 └─────────────────────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       ▼
                                 ┌─────────────────────────────────────────────────────────────────────────────┐
                                 │                          RUNTIME BRIDGE GATEWAY                             │
                                 │          (The Only Authorized Intelligence → Runtime Integration)           │
                                 └─────────────────────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       ▼
                                 ┌─────────────────────────────────────────────────────────────────────────────┐
                                 │                   RUNTIME OPERATING SYSTEM KERNEL (M5 — FROZEN)             │
                                 │  • DAG Task Execution         • Agent Swarms & Capabilities                 │
                                 │  • PlatformScheduler          • ResourceBroker & Cost Accounting            │
                                 │  • Execution Sessions         • Retry Policy & Circuit Breakers             │
                                 └─────────────────────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       ▼
                                 ┌─────────────────────────────────────────────────────────────────────────────┐
                                 │                  EXTERNAL CONNECTORS & PLUGINS ECOSYSTEM                    │
                                 │  • 29 Domain Modules          • 5 Sector Plugins (Restaurant, Retail, etc.) │
                                 │  • 13 Live Connectors         • Gemini Live AI Provider • Messaging API     │
                                 └─────────────────────────────────────────────────────────────────────────────┘
```

---

# Business Knowledge Graph & Ontology

BizOS models organizational knowledge using a formal typed graph ontology (`app/domain/knowledge/models.py`):

* **KnowledgeNode (10 Typed Entities)**:
  * `Employee`, `Department`, `Organization`, `Customer`, `Product`, `Project`, `Vendor`, `Asset`, `Document`, `WorkflowEntity`.
  * Each node supports semantic embedding references (`embedding_refs`), provenance tracking, and versioning.
* **KnowledgeEdge (9 Directed Relationships)**:
  * `REPORTS_TO`, `BELONGS_TO`, `MANAGES`, `OWNS`, `WORKS_ON`, `PURCHASED`, `DEPENDS_ON`, `RELATED_TO`, `PART_OF`.

---

# 29 Business Domain Modules & 5 Vertical Sector Plugins

BizOS has been certified across **29 horizontal and industry domain modules**, organized around **5 Vertical Sector Plugins**:

### Vertical Sector Plugins (`app/plugins/`)
1. **Restaurant** (`bella_vista@v1.0`) — *Bella Vista Group* restaurant management, kitchen workflows, & crisis simulation.
2. **Retail** (`apex_retail@v1.0`) — *Apex Retail Group* POS, omnichannel inventory, and retail operations.
3. **Healthcare** (`st_jude@v1.0`) — *St. Jude Medical Center* patient triage, compliance, and hospital workflows.
4. **Finance** (`pinnacle_wealth@v1.0`) — *Pinnacle Global Wealth* wealth management, compliance, and asset tracking.
5. **Manufacturing** (`titan_manufacturing@v1.0`) — *Titan Heavy Industries* shop floor automation, QC, & supply chain.

### Horizontal & Functional Domain Modules (29 Total)
* `restaurant`, `retail`, `healthcare`, `finance`, `manufacturing`, `supply_chain`, `crm`, `hr`, `inventory`, `procurement`, `sales`, `marketing`, `customer_support`, `operations`, `analytics`, `projects`, `compliance`, `legal`, `real_estate`, `hospitality`, `energy`, `transportation`, `pharma`, `insurance`, `agriculture`, `automotive`, `aerospace`, `construction`, `telecom`.

---

# Connectors & External Integrations (`app/connectors/`)

BizOS communicates with the external world through 13 dedicated, secure connector suites:

| Connector Suite | Description & Capabilities |
|-----------------|----------------------------|
| `whatsapp` | Live WhatsApp Business Cloud API messaging, interactive template broadcasting, and webhook ingestion. |
| `gmail` | Automated email dispatch, thread ingestion, and message parsing. |
| `google_calendar` | Multi-tenant schedule synchronization, event creation, and availability tracking. |
| `google_drive` | Cloud file storage, asset management, and document ingestion. |
| `google_workspace` | Unified Google Workspace enterprise automation. |
| `instagram` | Social media engagement, DM automation, and campaign broadcasting. |
| `banking_upi` | Secure financial transactions, UPI verification, and payment reconciliation. |
| `scheduler` | `PlatformScheduler` with time-aware cron execution, polling, and exponential backoff with retry jitter. |
| `webhooks` | High-throughput inbound/outbound event gateway with signature verification. |
| `auth` | Multi-tenant authentication and API key governance. |
| `auditor` | Telemetry, event auditing, and compliance log collectors. |
| `runtime` | Distributed worker role and transport adapters (`InProcessTransport`). |
| `sdk` | Python and client SDK bridge bindings. |

---

# Complete Roadmap: Wave 0 (M0–M6) to Wave 24

| Wave / Milestone | Focus Area | Status & Certification |
|------------------|------------|------------------------|
| **Wave 0 (M0–M6)** | **The AI OS Foundation (Milestones M0 to M6)**<br>• **M0**: Core Async Scaffolding & Foundational Architecture<br>• **M1**: Digital Twin State Modeling & Drift Detection (`Supabase`)<br>• **M2**: Semantic Memory Engine (`Qdrant`), Episodic Memory & Cognitive Traces<br>• **M3**: AI Provider Kernel (`GeminiProvider`, Structured Intent Classification)<br>• **M4**: Context Engine (`EnterpriseContext`) & Knowledge Graph Ontology (`KnowledgeNode`/`KnowledgeEdge`)<br>• **M5**: **Runtime OS Kernel (FROZEN)** — DAG Task Engine, Agent Registry, Budgets, Retry Policies<br>• **M6**: **Executive Intelligence Kernel (FROZEN)** — Strategic Goal Manager, AI Planning, Compliance | ✅ **COMPLETED & FROZEN** (v6.0.0) |
| **Waves 1–3** | Core Domain Modeling, Multi-Tenant Security & Workspace Isolation, and Foundational Runtime Infrastructure | ✅ Certified |
| **Waves 4–6** | Cognitive Substrates, Advanced Reasoning & Planning Engine, Copilot / Worker Execution, and Insights | ✅ Certified |
| **Wave 7 & 7.5** | Human-in-the-Loop (HITL) Approval Workflows and Autonomous Agent Pluggable Capabilities (`CapabilityRegistry`) | ✅ Certified |
| **Wave 8** | Multi-Agent Collaboration & Swarm Orchestration — Cross-agent communication & collaborative problem-solving | ✅ Certified |
| **Waves 9–11** | Vertical Sector Plugins (5 Sectors) & 29 Horizontal Business Domain Modules | ✅ Certified |
| **Wave 12** | Architectural Hardening & Production Immutability Contracts (Strict one-way Runtime Bridge enforcement) | ✅ Certified |
| **Wave 13** | Production Deployment & Edge-Case Certification (522-case matrix, Level 5 Autonomous AI OS) | ✅ Certified |
| **Wave 14** | **Platform Maturity Enhancements** — `ResourceBroker`, cost accounting, distributed runtime, `TimeTravelInspector`, automatic `ExecutionMode` propagation (`SIMULATION`/`DRY_RUN`/`PRODUCTION`), API-First `MetricsService` | ✅ Certified (`demo_wave14_maturity.py`) |
| **Waves 15–24** | Phased Enterprise Certification Suites, Chaos Engineering, Adaptive Context Compression, Kafka/Pulsar Event Ordering, & Continuous Regression Suites | ✅ Continuous Certification (`tests/certification/`) |

---

# Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12+ |
| Runtime | asyncio |
| API | FastAPI |
| Validation | Pydantic v2 |
| AI Providers | Google Gemini (Gemini Live Provider), extensible |
| Database | PostgreSQL (Supabase) |
| Vector Store | Qdrant |
| Logging & Telemetry | Structlog, OpenTelemetry (`TelemetryTracker`) |
| Testing | Pytest, Hypothesis (Property-based), Syrupy |
| Package Manager | uv |

---

# Project Structure

```text
bizos/
├── app/
│   ├── bootstrap/          # Dependency injection container & application wiring
│   ├── connectors/         # 13 external connectors (whatsapp, gmail, scheduler, etc.)
│   ├── core/               # Core resource brokerage & cost accounting
│   ├── domain/             # Domain models (knowledge graph, twin, goals, tasks)
│   ├── infrastructure/     # Supabase, Qdrant, Gemini AI, observability, plugins
│   ├── intelligence/       # M6 Executive Intelligence Kernel (FROZEN)
│   ├── interfaces/         # REST API (v1), CLI, SDK
│   ├── platform/           # Configuration, dashboard metrics, health services
│   ├── runtime/            # M5 Runtime OS Kernel & Runtime Bridge (FROZEN)
│   └── shared/             # Cross-cutting primitives & ExecutionMode enums
├── app/plugins/            # 5 Vertical Sector Plugins (restaurant, retail, etc.)
├── docs/                   # Architecture, ADRs, developer guides, milestone summaries
├── migrations/             # SQL schema migrations
├── scripts/                # Master certification and edge-case validation scripts
├── tests/                  # Unit, integration, regression, and certification suites
├── README.md
└── pyproject.toml
```

---

# Getting Started

## Prerequisites

- Python 3.12+
- uv
- Supabase (PostgreSQL)
- Qdrant (Vector Store)

## Installation

```bash
git clone https://github.com/your-org/bizos.git
cd bizos
uv sync
cp .env.example .env
```

Configure your environment variables in `.env`.

## Run Locally

```bash
docker compose up -d
uv run uvicorn app.main:app --reload
```

Health check:

```bash
curl http://localhost:8000/health
```

---

# Testing & Certification

Run all unit & integration tests:

```bash
uv run pytest
```

Execute the Continuous Regression Suite (Waves 15–24 & Wave 14 Maturity):

```bash
uv run pytest tests/certification/ -v
uv run python demo_wave14_maturity.py
```

Run the Master 522-Cell Edge Case Certification Suite:

```bash
uv run python scripts/bizos_master_certification_suite.py
```

---

# Documentation

- 📘 [System Architecture Overview](SYSTEM_OVERVIEW.md)
- 📗 [Impossible & Edge Case Certification Report](impossible_edge_case_report.md)
- 📙 [Milestone Summaries (M4–M6)](docs/milestones/)
- 📕 Architecture Decision Records (ADRs) under `docs/architecture/decisions/`

---

# Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

---

# Security

Please read [SECURITY.md](SECURITY.md) before reporting vulnerabilities.

---

# License

MIT License — see [LICENSE](LICENSE) for details.
