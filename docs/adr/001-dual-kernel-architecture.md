# ADR-001: Dual-Kernel Architecture

**Status:** Accepted | **Date:** 2026-06-28

## Context
Early BizOS versions conflated execution concerns (how agents do things) with intelligence concerns (what agents should do) in a single service layer, leading to tight coupling and brittle evolution.

## Decision
Separate BizOS into two isolated kernels: M5 Runtime OS Kernel (execution substrate) and M6 Executive Intelligence Kernel (cognitive substrate). Communication is exclusively through a typed Runtime Bridge. Direct cross-kernel imports are prohibited.

## Consequences
- Each kernel can evolve, be tested, and deployed independently
- Bridge interface is the only stable API surface between kernels
- Initial complexity justified by long-term scalability and isolation
