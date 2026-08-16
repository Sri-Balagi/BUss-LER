"""BizOS Module SDK Public Entrypoint."""

from app.core.modules.base import (
    BaseModule,
    BusinessModule,
    DomainModule,
    HorizontalModule,
    VerticalModule,
)
from app.core.modules.contracts.contracts import (
    ICustomerProvider,
    IInventoryProvider,
    INotificationProvider,
    IPaymentProvider,
    IWorkflowProvider,
)
from app.core.modules.discovery.discovery import (
    CapabilityDiscoveryRegistry,
    ModuleCapabilityDescriptor,
)
from app.core.modules.extension_points.extension_points import (
    ExtensionHook,
    ExtensionPointRegistry,
    ModuleExtensionPoint,
)
from app.core.modules.kernel.kernel_models import (
    Address,
    AuditContext,
    Contact,
    Currency,
    Customer,
    EntityReference,
    Money,
    Organization,
    TaxInfo,
)
from app.core.modules.lifecycle import ModuleLifecycleState, ModuleState
from app.core.modules.manager import ModuleDependencyResolver, ModuleManager
from app.core.modules.models import (
    MarketplaceMetadata,
    ModuleCapabilities,
    ModuleCategory,
    ModuleConfiguration,
    ModuleContext,
    ModuleManifest,
    ModuleMetadata,
    ModuleType,
)
from app.core.modules.registry import ModuleRegistry

__all__ = [
    "BaseModule",
    "BusinessModule",
    "VerticalModule",
    "HorizontalModule",
    "DomainModule",
    "ModuleManifest",
    "ModuleMetadata",
    "ModuleConfiguration",
    "ModuleContext",
    "ModuleCapabilities",
    "MarketplaceMetadata",
    "ModuleCategory",
    "ModuleType",
    "ModuleState",
    "ModuleLifecycleState",
    "ModuleRegistry",
    "ModuleManager",
    "ModuleDependencyResolver",
    "CapabilityDiscoveryRegistry",
    "ModuleCapabilityDescriptor",
    "ExtensionPointRegistry",
    "ModuleExtensionPoint",
    "ExtensionHook",
    "Customer",
    "Organization",
    "Money",
    "Address",
    "Contact",
    "TaxInfo",
    "AuditContext",
    "EntityReference",
    "Currency",
    "ICustomerProvider",
    "IInventoryProvider",
    "IPaymentProvider",
    "IWorkflowProvider",
    "INotificationProvider",
]
