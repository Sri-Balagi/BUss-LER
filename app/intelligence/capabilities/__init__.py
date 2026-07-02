"""
Intelligence Capabilities Namespace (Reserved for Wave 1)

This module reserves the namespace for the R3 evolution (reasoning, reflection, refinement)
and capability-based architectures that will be fully implemented in Wave 1.
We are intentionally deferring the actual capability design to maintain focus on the
foundational AI infrastructure in Wave 0.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ICapability(Protocol):
    """
    Base protocol for AI capabilities.

    # TODO: Wave 1 — do not implement here.
    This interface serves merely as a structural placeholder for the upcoming
    capability architecture.
    """

    pass
