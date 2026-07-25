"""Integration & validation test suite for the BizOS Connector Ecosystem Platform."""
import pytest
from app.bootstrap.container import Container
from app.connectors.registry.manifest import ConnectorManifest, CapabilityDeclaration, AuthType, SyncType
from app.connectors.registry.registry import ConnectorRegistry, get_registry
from app.connectors.registry.loader import ConnectorLoader
from app.connectors.manager.manager import ConnectorManager
from app.connectors.manager.health import HealthMonitor
from app.connectors.capabilities.registry import CapabilityRegistry, ConnectorCapabilityModel
from app.connectors.tools.registry import ToolRegistry, ConnectorTool, ToolParameter
from app.connectors.secrets.models import SecretRecord, SecretType
from app.connectors.secrets.vault import InMemorySecretVault
from app.connectors.state.models import ConnectorState
from app.connectors.state.store import InMemoryStateStore
from app.connectors.ratelimit.limiter import RateLimiter
from app.connectors.retry.executor import RetryExecutor, RetryPolicy
from app.connectors.canonical.message import CanonicalMessage
from app.connectors.canonical.rich_message import CanonicalRichMessage, CanonicalButton
from app.connectors.builtin.github.connector import GitHubConnector
from app.connectors.builtin.communication.whatsapp.connector import WhatsAppConnector
from pydantic import SecretStr


@pytest.fixture
def registry() -> ConnectorRegistry:
    reg = ConnectorRegistry()
    loader = ConnectorLoader(reg)
    loader.load_all()
    return reg


@pytest.fixture
def manager(registry: ConnectorRegistry) -> ConnectorManager:
    health = HealthMonitor()
    mgr = ConnectorManager(registry, health)
    mgr.register_factory("github", GitHubConnector)
    mgr.register_factory("whatsapp", WhatsAppConnector)
    return mgr


def test_registry_loading(registry: ConnectorRegistry) -> None:
    """Verify registry discovers and registers all builtin connectors."""
    assert registry.count >= 10
    assert registry.exists("github")
    assert registry.exists("whatsapp")
    assert registry.exists("slack")
    assert registry.exists("telegram")


def test_manifest_validation(registry: ConnectorRegistry) -> None:
    """Verify manifests are structurally valid."""
    gh_manifest = registry.get("github")
    assert gh_manifest.id == "github"
    assert gh_manifest.auth_type == AuthType.OAUTH2
    assert len(gh_manifest.capabilities) >= 1
    assert gh_manifest.ai_metadata.description != ""


@pytest.mark.asyncio
async def test_connector_lifecycle(manager: ConnectorManager) -> None:
    """Verify complete guided installation lifecycle."""
    inst = GitHubConnector("github", "test_profile", client_id="cid", client_secret="csec", auth_url="http://auth", token_url="http://token")
    manager._instances["github:test_profile"] = inst
    await inst.install()
    assert inst.status.value == "INSTALLED"


@pytest.mark.asyncio
async def test_secret_vault() -> None:
    """Verify secret storage and masking."""
    vault = InMemorySecretVault()
    secret = SecretRecord(
        secret_id="s1",
        connector_id="github",
        secret_type=SecretType.OAUTH_TOKEN,
        value=SecretStr("ghp_secret_token_12345"),
    )
    await vault.store("github:default:creds", secret)
    retrieved = await vault.retrieve("github:default:creds")
    assert retrieved is not None
    assert retrieved.value.get_secret_value() == "ghp_secret_token_12345"
    assert retrieved.masked_display() == "ghp_***2345"


@pytest.mark.asyncio
async def test_state_store() -> None:
    """Verify state persistence across reloads."""
    store = InMemoryStateStore()
    state = ConnectorState(
        connector_id="github",
        profile_id="default",
        cursor="cursor_v1",
        checkpoint={"last_id": 42},
    )
    await store.save(state)
    loaded = await store.load("github", "default")
    assert loaded.cursor == "cursor_v1"
    assert loaded.checkpoint == {"last_id": 42}


@pytest.mark.asyncio
async def test_rate_limiter() -> None:
    """Verify token bucket rate limiter execution."""
    limiter = RateLimiter.token_bucket(capacity=10, refill_rate=100.0)
    await limiter.acquire(1)
    status = limiter.quota_status()
    assert status.remaining <= 10


@pytest.mark.asyncio
async def test_messaging_connector_execution(manager: ConnectorManager) -> None:
    """Verify messaging connector execution and canonical model output."""
    wa = WhatsAppConnector("whatsapp", "default")
    manager._instances["whatsapp:default"] = wa
    msg = await wa.send_message(recipient_id="+1234567890", content="Hello BizOS")
    assert isinstance(msg, CanonicalMessage)
    assert msg.source_connector == "whatsapp"
    assert msg.content == "Hello BizOS"


def test_capability_registry() -> None:
    """Verify capability registration and discovery."""
    cap_reg = CapabilityRegistry()
    cap_reg.register(
        ConnectorCapabilityModel(
            capability_id="communication.messaging.send_message",
            name="Send Message",
            connector_id="whatsapp",
            operations=["send_message"],
        )
    )
    connectors = cap_reg.find_connectors_for_operation("send_message")
    assert "whatsapp" in connectors


def test_tool_registry() -> None:
    """Verify ToolRegistry definition and lookup."""
    tool_reg = ToolRegistry()
    tool_reg.register_tool(
        ConnectorTool(
            tool_id="whatsapp.send_message",
            connector_id="whatsapp",
            capability_id="communication.messaging.send_message",
            name="send_message",
            description="Send a message to a WhatsApp user",
            parameters=[
                ToolParameter(name="recipient_id", type="string", description="Phone number"),
                ToolParameter(name="content", type="string", description="Message text"),
            ],
        )
    )
    tool = tool_reg.get_tool("whatsapp.send_message")
    assert tool.name == "send_message"
    assert len(tool.parameters) == 2
