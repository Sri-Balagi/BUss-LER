from datetime import UTC, datetime, timedelta, timezone

import jwt
import pytest

from app.application.security.auth_service import AuthenticationService
from app.domain.identity.api_key import APIKey, APIKeyStatus
from app.domain.security.config import SecurityConfig
from app.domain.security.models import AuthenticationStatus, ExecutionContext
from app.infrastructure.persistence.memory.api_key_repository import InMemoryAPIKeyRepository
from app.infrastructure.security.hashers import BcryptHasher
from app.infrastructure.security.providers.api_key_provider import APIKeyIdentityProvider
from app.infrastructure.security.providers.jwt_provider import JWTIdentityProvider


@pytest.fixture
def security_config():
    return SecurityConfig(
        encryption_key=b'0'*32,
        bcrypt_rounds=4,
        token_length_bytes=32,
        jwt_keys={"default": "secret_key", "other": "other_secret"}
    )

@pytest.fixture
def hasher(security_config):
    return BcryptHasher(rounds=security_config.bcrypt_rounds)

@pytest.fixture
def jwt_provider(security_config):
    return JWTIdentityProvider(config=security_config)

@pytest.fixture
def api_key_repo():
    return InMemoryAPIKeyRepository()

@pytest.fixture
def api_key_provider(api_key_repo, hasher):
    return APIKeyIdentityProvider(repo=api_key_repo, hasher=hasher)

@pytest.fixture
def auth_service(jwt_provider, api_key_provider):
    return AuthenticationService(providers=[jwt_provider, api_key_provider])


@pytest.mark.asyncio
async def test_jwt_provider_success(jwt_provider):
    token = jwt.encode(
        {"sub": "user_123", "tenant_id": "tenant_1", "exp": datetime.now(UTC) + timedelta(minutes=15)},
        "secret_key",
        algorithm="HS256",
        headers={"kid": "default"}
    )

    result = await jwt_provider.authenticate(token)
    assert result.status == AuthenticationStatus.SUCCESS
    assert result.context is not None
    assert result.context.is_authenticated is True
    assert result.context.user_id == "user_123"
    assert result.context.tenant_id == "tenant_1"
    assert result.context.authentication_method == "jwt"

@pytest.mark.asyncio
async def test_jwt_provider_invalid_signature(jwt_provider):
    token = jwt.encode(
        {"sub": "user_123"},
        "wrong_secret",
        algorithm="HS256",
        headers={"kid": "default"}
    )
    result = await jwt_provider.authenticate(token)
    assert result.status == AuthenticationStatus.INVALID_TOKEN
    assert result.context is None

@pytest.mark.asyncio
async def test_jwt_provider_expired(jwt_provider):
    token = jwt.encode(
        {"sub": "user_123", "exp": datetime.now(UTC) - timedelta(minutes=15)},
        "secret_key",
        algorithm="HS256",
        headers={"kid": "default"}
    )
    result = await jwt_provider.authenticate(token)
    assert result.status == AuthenticationStatus.TOKEN_EXPIRED
    assert result.context is None

@pytest.mark.asyncio
async def test_jwt_provider_unknown_kid(jwt_provider):
    token = jwt.encode(
        {"sub": "user_123"},
        "secret_key",
        algorithm="HS256",
        headers={"kid": "unknown"}
    )
    result = await jwt_provider.authenticate(token)
    assert result.status == AuthenticationStatus.AUTHENTICATION_FAILED
    assert result.context is None

@pytest.mark.asyncio
async def test_api_key_provider_success(api_key_provider, api_key_repo, hasher):
    raw_key = "abc12345.restofkey"
    hashed_key = hasher.hash(raw_key)

    key_record = APIKey(
        name="Test Key",
        key_hash=hashed_key,
        prefix="abc12345",
        status=APIKeyStatus.ACTIVE
    )
    await api_key_repo.save(key_record)

    result = await api_key_provider.authenticate(raw_key)
    assert result.status == AuthenticationStatus.SUCCESS
    assert result.context is not None
    assert result.context.is_authenticated is True
    assert result.context.api_key_id == str(key_record.id)
    assert result.context.authentication_method == "api_key"

@pytest.mark.asyncio
async def test_api_key_provider_wrong_hash(api_key_provider, api_key_repo, hasher):
    raw_key = "abc12345.wrong"
    hashed_key = hasher.hash("abc12345.correct")

    key_record = APIKey(
        name="Test Key",
        key_hash=hashed_key,
        prefix="abc12345",
        status=APIKeyStatus.ACTIVE
    )
    await api_key_repo.save(key_record)

    result = await api_key_provider.authenticate(raw_key)
    assert result.status == AuthenticationStatus.INVALID_TOKEN
    assert result.context is None

@pytest.mark.asyncio
async def test_api_key_provider_revoked(api_key_provider, api_key_repo, hasher):
    raw_key = "abc12345.restofkey"
    hashed_key = hasher.hash(raw_key)

    key_record = APIKey(
        name="Test Key",
        key_hash=hashed_key,
        prefix="abc12345",
        status=APIKeyStatus.REVOKED
    )
    await api_key_repo.save(key_record)

    result = await api_key_provider.authenticate(raw_key)
    assert result.status == AuthenticationStatus.REVOKED
    assert result.context is None

@pytest.mark.asyncio
async def test_auth_service_routing(auth_service, api_key_repo, hasher):
    # Test JWT route
    token = jwt.encode(
        {"sub": "user_123", "exp": datetime.now(UTC) + timedelta(minutes=15)},
        "secret_key",
        algorithm="HS256",
        headers={"kid": "default"}
    )

    result = await auth_service.authenticate("Bearer", token)
    assert result.status == AuthenticationStatus.SUCCESS
    assert result.context.is_authenticated is True
    assert result.context.user_id == "user_123"

    # Test API Key route
    raw_key = "abc12345.restofkey"
    hashed_key = hasher.hash(raw_key)
    await api_key_repo.save(APIKey(
        name="Test Key",
        key_hash=hashed_key,
        prefix="abc12345"
    ))

    result2 = await auth_service.authenticate("ApiKey", raw_key)
    assert result2.status == AuthenticationStatus.SUCCESS
    assert result2.context.is_authenticated is True
    assert result2.context.authentication_method == "api_key"

    # Test unknown scheme
    result3 = await auth_service.authenticate("Unknown", "token")
    assert result3.status == AuthenticationStatus.UNSUPPORTED_SCHEME
    assert result3.context is None
