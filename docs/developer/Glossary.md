# BizOS Glossary

- **Entity:** A unique identity representing a person, company, sensor, or concept. The relational anchor.
- **Digital Twin:** The dynamic, schemaless representation of an Entity's current state and metadata at a specific point in time.
- **Memory:** Vectorized representations of the Twin's past, stored in Qdrant for semantic retrieval.
- **Goal:** A defined "Desired State" the system or agent is attempting to steer the Digital Twin toward.
- **Context:** The intelligently assembled prompt payload (Twin State + Memories + Goals) injected into the LLM context window.
- **Simulation:** A sandboxed environment where cloned Twins are fast-forwarded through time using Agents to predict outcomes.
- **Reflection:** A background AI process that abstracts specific Episodic Memories into general Semantic Knowledge.
- **Event:** A discrete occurrence in the system (e.g., `TwinUpdated`), published to the Event Bus.
- **Agent:** An autonomous or semi-autonomous AI worker that consumes events, reasons, and executes actions.
- **Embedding:** A high-dimensional vector array representing the semantic meaning of text/memory.
- **AI Kernel:** The abstraction layer managing LLM routing, prompting, and safety.
- **Workspace / Organization:** Multi-tenant hierarchy groupings for isolation and permissions.
