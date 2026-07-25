"""
BizOS Connector Ecosystem.

The Connector Platform is the integration layer for BizOS, enabling hundreds
of enterprise integrations through a common SDK, registry, lifecycle manager,
authentication framework, sync engine, webhook infrastructure, and AI tool layer.

Architecture:
    Connector SDK  →  Registry  →  Manager  →  Business Modules / AI Agents

Namespace:
    All connector domain events are published on the SystemBus under the
    ``connector.*`` topic prefix.
"""

__version__ = "2.0.0"
