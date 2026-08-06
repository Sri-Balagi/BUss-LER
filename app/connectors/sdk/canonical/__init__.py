"""BizOS Canonical Business SDK — Modular Package.

This package provides backward-compatible re-exports from the original
monolithic `canonical.py` module (now `canonical_legacy.py`) so all
existing connectors importing from `app.connectors.sdk.canonical` continue
to work without modification.

New connector code should import from the domain-specific sub-modules:
  from app.connectors.sdk.canonical.crm import CanonicalContact
  from app.connectors.sdk.canonical.common import CanonicalAssociation
"""

# ── Backward-compatible re-exports from the legacy monolithic module ──────────
# All symbols that existing connectors rely on are exported here.
from app.connectors.sdk.canonical_legacy import (   # noqa: F401
    CanonicalUser,
    CanonicalPage,
    CanonicalEmail,
    CanonicalMessage,
    CanonicalContact,
    CanonicalFile,
    CanonicalFolder,
    CanonicalDrive,
    CanonicalPermission,
    CanonicalRevision,
    CanonicalComment,
    CanonicalDeltaChange,
    CanonicalWebhookSubscription,
    CanonicalDriveActivity,
    CanonicalCalendar,
    CanonicalCalendarAttachment,
    CanonicalCalendarEvent,
    CanonicalFreeBusy,
    CanonicalSharePointSite,
    CanonicalSharePointList,
    CanonicalSharePointListItem,
    CanonicalNotionUser,
    CanonicalNotionPage,
    CanonicalNotionDatabase,
    CanonicalNotionBlock,
    CanonicalFinancialAccount,
    CanonicalTransaction,
    CanonicalPayment,
)

# ── New modular Business SDK symbols ─────────────────────────────────────────
from app.connectors.sdk.canonical.common import (   # noqa: F401
    CanonicalAssociation,
    AssociationType,
)
from app.connectors.sdk.canonical.crm import (      # noqa: F401
    CanonicalContact as CanonicalCRMContact,
    CanonicalCompany,
    CanonicalDeal,
    CanonicalStage,
    CanonicalPipeline,
    CanonicalTask,
    CanonicalNote,
    CanonicalActivity,
    CanonicalActivityType,
    CanonicalProduct,
    CanonicalOwner,
)
